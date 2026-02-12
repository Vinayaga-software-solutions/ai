<?php

use Livewire\Component;
use Livewire\WithFileUploads; // Required for file handling
use App\Models\Project;
use App\Models\DataCollection;
use App\Models\Data;
use Illuminate\Validation\Rule;

new class extends Component {
    use WithFileUploads;

    public string $name = '';
    public string $description = '';
    public string $type = 'document';
    public ?int $data_collection_id = null;
    public string $storage_path = '';
    public $file; // Temporary file storage

    public function mount()
    {
        $this->data_collection_id = request('data_collection_id') ?? DataCollection::query()->first()?->id;
    }

    public function with(): array
    {
        return [
            'collections' => DataCollection::with('project')->get(),
        ];
    }

    public function save()
    {
        $rules = [
            'data_collection_id' => 'required|exists:data_collections,id',
            'name' => ['required', 'max:255', Rule::unique('data', 'name')->where('data_collection_id', $this->data_collection_id)],
            'type' => 'required|in:document,table,json',
            'description' => 'nullable|max:2000',
        ];

        // Add file validation if type is document
        if ($this->type === 'document') {
            $rules['file'] = 'required|file|max:10240'; // 10MB limit
        } else {
            $rules['storage_path'] = 'required|max:255';
        }

        $validated = $this->validate($rules);

        $finalPath = $this->storage_path;

        // Handle File Upload for Documents
        if ($this->type === 'document' && $this->file) {
            // Determine disk based on environment (local vs gcs)
            $disk = config('filesystems.default');
            // Storage::disk('gcs')->put('test.txt', 'Hello from Laravel!');

            // Generate a clean path: tensrgrid/documents/{collection_id}/{filename}
            $directory = "tensrgrid/documents/{$this->data_collection_id}";
            $finalPath = $this->file->store($directory, $disk);
        }

        Data::create([
            'data_collection_id' => $validated['data_collection_id'],
            'name' => $validated['name'],
            'description' => $validated['description'] ?? null,
            'type' => $validated['type'],
            'storage_path' => $finalPath,
            'created_by' => auth()->id(),
        ]);

        Flux::toast('Data source initialized successfully.');

        return $this->redirect('/data', navigate: true);
    }
};
?>

<div class="max-w-lg">
    @if ($collections->isEmpty())
        {{-- Empty state code remains the same --}}
    @else
        <flux:heading size="xl" level="1">Initialize Data Source</flux:heading>
        <flux:subheading>Define the storage and format for your new data stream.</flux:subheading>

        <form wire:submit="save" class="mt-6 space-y-6">
            <flux:select wire:model="data_collection_id" label="Data Collection" required searchable>
                @foreach ($collections as $collection)
                    <flux:select.option :value="$collection->id">
                        {{ $collection->project->name }} / {{ $collection->name }}
                    </flux:select.option>
                @endforeach
            </flux:select>

            <flux:radio.group wire:model.live="type" label="Data Type" variant="cards" class="flex flex-col">
                <flux:radio value="document" label="Document" description="Upload PDF, TXT, or Docs" />
                <flux:radio value="table" label="Table" description="Structured rows (SQL/BigQuery)" />
                <flux:radio value="json" label="JSON" description="Semi-structured (NoSQL/JSON)" />
            </flux:radio.group>

            <flux:input wire:model="name" label="Source Name" placeholder="e.g. Q4 Financials" required />

            {{-- Conditional UI: File Upload for Documents, Text input for others --}}
            @if ($type === 'document')
                <flux:field>
                    <flux:label>Upload Document</flux:label>

                    <div x-data="{ isUploading: false, progress: 0, isDropped: false }" x-on:livewire-upload-start="isUploading = true"
                        x-on:livewire-upload-finish="isUploading = false; isDropped = true"
                        x-on:livewire-upload-error="isUploading = false"
                        x-on:livewire-upload-progress="progress = $event.detail.progress" class="relative mt-2">
                        {{-- Drag & Drop Zone --}}
                        <label for="file-upload"
                            class="flex flex-col items-center justify-center w-full h-40 border-2 border-dashed rounded-xl cursor-pointer transition-colors
                    {{ $errors->has('file') ? 'border-red-300 bg-red-50 dark:bg-red-900/10' : 'border-zinc-300 bg-zinc-50 hover:bg-zinc-100 dark:border-zinc-700 dark:bg-zinc-900 dark:hover:bg-zinc-800' }}">
                            <div class="flex flex-col items-center justify-center pt-5 pb-6">
                                {{-- Icon switches based on state --}}
                                <template x-if="!isUploading && !isDropped">
                                    <flux:icon.cloud-arrow-up class="size-10 text-zinc-400 mb-3" />
                                </template>

                                {{-- Uploading Spinner --}}
                                <template x-if="isUploading">
                                    <div class="mb-3">
                                        <svg class="animate-spin h-10 w-10 text-indigo-600"
                                            xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24">
                                            <circle class="opacity-25" cx="12" cy="12" r="10"
                                                stroke="currentColor" stroke-width="4"></circle>
                                            <path class="opacity-75" fill="currentColor"
                                                d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z">
                                            </path>
                                        </svg>
                                    </div>
                                </template>

                                {{-- Success State --}}
                                <template x-if="isDropped && !isUploading">
                                    <flux:icon.check-circle variant="solid" class="size-10 text-green-500 mb-3" />
                                </template>

                                <p class="mb-2 text-sm text-zinc-700 dark:text-zinc-300">
                                    <span class="font-semibold"
                                        x-text="isUploading ? 'Uploading...' : (isDropped ? 'File Ready' : 'Click to upload')"></span>
                                </p>
                                <p class="text-xs text-zinc-500"
                                    x-text="isUploading ? progress + '%' : 'PDF, TXT, or DOC (MAX. 10MB)'"></p>
                            </div>

                            <input id="file-upload" type="file" wire:model="file" class="hidden"
                                accept=".pdf,.txt,.doc,.docx,.md" />
                        </label>

                        {{-- Validation Error --}}
                        <flux:error name="file" />

                        {{-- Progress Bar (Overlay) --}}
                        <div x-show="isUploading"
                            class="absolute inset-x-0 bottom-0 h-1 bg-zinc-200 overflow-hidden rounded-b-xl">
                            <div class="bg-indigo-600 h-full transition-all duration-200"
                                :style="'width: ' + progress + '%'"></div>
                        </div>
                    </div>
                </flux:field>
            @else
                <flux:input wire:model="storage_path" label="Storage Reference"
                    :placeholder="$type === 'table' ? 'database_table_name' : 'nosql_collection_name'" required />
            @endif

            <flux:textarea wire:model="description" label="Description" rows="3" />

            <div class="flex justify-end gap-3">
                <flux:button href="history.back()" variant="ghost" wire:navigate>Cancel</flux:button>
                <flux:button type="submit" variant="primary" wire:loading.attr="disabled" wire:target="file, save">
                    <span wire:loading.remove wire:target="file">Initialize Data</span>
                    <span wire:loading wire:target="file">Uploading...</span>
                    <span wire:loading wire:target="save">Processing...</span>
                </flux:button>
            </div>
        </form>
    @endif
</div>
