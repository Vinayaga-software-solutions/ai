<?php

use Livewire\Component;
use Livewire\WithFileUploads;
use Livewire\WithPagination; //
use App\Models\Data;
use Flux\Flux;

new class extends Component {
    use WithFileUploads, WithPagination; //

    public Data $data;
    public string $fileSearch = '';
    public $newFiles = []; 

    // Reset pagination when search changes
    public function updatedFileSearch()
    {
        $this->resetPage();
    }

    public function mount(Data $data)
    {
        $this->data = $data->load(['dataCollection.project', 'creator']);
    }

    /**
     * Fetch paginated files.
     * Note: In Flux, we use :paginate="$items" on the table.
     */
    public function with(): array
    {
        return [
            'files' => $this->data->files()
                ->when($this->fileSearch, function ($query) {
                    $query->where('original_name', 'like', '%' . $this->fileSearch . '%');
                })
                ->latest()
                ->paginate(10), //
        ];
    }

    public function updatedNewFiles()
    {
        $this->validate([
            'newFiles.*' => 'file|max:10240', 
        ]);

        $count = count($this->newFiles);

        foreach ($this->newFiles as $file) {
            $path = $file->store($this->data->storage_path, config('filesystems.default'));

            $this->data->files()->create([
                'original_name' => $file->getClientOriginalName(),
                'storage_path' => $path,
                'mime_type' => $file->getMimeType(),
                'size' => $file->getSize(),
            ]);
        }

        $this->newFiles = [];
        $this->resetPage(); //
        
        Flux::toast("$count files added successfully.");
    }

    public function delete()
    {
        $this->data->delete();
        Flux::toast('Data source deleted.');
        return $this->redirect('/data', navigate: true);
    }
}; ?>

<div class="space-y-8 max-w-4xl mx-auto py-10">
    {{-- Actions --}}
    <div class="flex items-center justify-between">
        <flux:button variant="ghost" icon="arrow-left" onclick="history.back()" class="-ml-3">Back</flux:button>
        <div class="flex items-center gap-2">
            <flux:button :href="'/data/'.$data->id.'/edit'" variant="ghost" icon="pencil-square" wire:navigate>Edit</flux:button>
            <flux:button variant="ghost" icon="trash" class="text-red-500" wire:click="delete" wire:confirm="Delete everything?" />
        </div>
    </div>

    {{-- Header --}}
    <div class="flex items-start gap-5">
        <div class="p-4 bg-zinc-100 dark:bg-zinc-800 rounded-2xl text-indigo-600">
            <flux:icon.document-text class="size-10" />
        </div>
        <div class="flex-1">
            <div class="flex items-center gap-3">
                <flux:heading size="xl">{{ $data->name }}</flux:heading>
                <flux:badge color="indigo" size="sm" inset="top bottom">{{ ucfirst($data->type) }}</flux:badge>
            </div>
            <flux:text class="mt-1">{{ $data->description ?: 'No description.' }}</flux:text>
        </div>
    </div>

    <flux:separator variant="subtle" />

    {{-- Info Grid --}}
    <div class="grid grid-cols-1 md:grid-cols-2 gap-8">
        <section class="space-y-4">
            <flux:heading size="md">Context</flux:heading>
            <div class="space-y-3 text-sm">
                <div class="flex justify-between border-b border-zinc-100 dark:border-zinc-800 pb-2">
                    <span class="text-zinc-500">Project</span>
                    <flux:link href="/project/{{ $data->dataCollection->project->id }}/detail" wire:navigate>{{ $data->dataCollection->project->name }}</flux:link>
                </div>
                <div class="flex justify-between">
                    <span class="text-zinc-500">Created By</span>
                    <span class="font-medium">{{ $data->creator->name }}</span>
                </div>
            </div>
        </section>

        {{-- <section class="space-y-4">
            <flux:heading size="md">Storage Reference</flux:heading>
            <div class="p-4 bg-zinc-50 dark:bg-zinc-900 border border-zinc-200 dark:border-zinc-800 rounded-xl">
                <flux:label>Root Path</flux:label>
                <div class="mt-2 flex items-center gap-2">
                    <code class="text-xs font-mono text-indigo-600 break-all">{{ $data->storage_path }}</code>
                </div>
            </div>
        </section> --}}
    </div>

    {{-- Files Section --}}
    @if($data->type === 'document')
        <section class="space-y-4" 
            x-data="{ isUploading: false, progress: 0 }" 
            x-on:livewire-upload-start="isUploading = true"
            x-on:livewire-upload-finish="isUploading = false"
            x-on:livewire-upload-error="isUploading = false"
            x-on:livewire-upload-progress="progress = $event.detail.progress">
            
            <div class="flex items-center justify-between">
                <flux:heading size="md">Managed Files</flux:heading>
                <div class="flex items-center gap-2">
                    <flux:input wire:model.live.debounce.300ms="fileSearch" view="search" placeholder="Search..." size="sm" class="w-48" />
                    <input type="file" id="add-files" wire:model="newFiles" multiple class="hidden">
                    <flux:button variant="subtle" size="sm" icon="plus" onclick="document.getElementById('add-files').click()" wire:loading.attr="disabled" wire:target="newFiles">
                        Add Files
                    </flux:button>
                </div>
            </div>

            <div x-show="isUploading" x-cloak class="w-full bg-zinc-100 dark:bg-zinc-800 rounded-full h-1.5 mb-4 overflow-hidden">
                <div class="bg-indigo-600 h-1.5 transition-all duration-300" :style="'width: ' + progress + '%'"></div>
            </div>

            <div class="bg-white dark:bg-zinc-900 border border-zinc-200 dark:border-zinc-800 rounded-xl overflow-hidden">
                {{-- --}}
                <flux:table :paginate="$files">
                    <flux:table.columns>
                        <flux:table.column>File Name</flux:table.column>
                        <flux:table.column>Size</flux:table.column>
                        <flux:table.column>Uploaded</flux:table.column>
                        <flux:table.column></flux:table.column>
                    </flux:table.columns>

                    <flux:table.rows>
                        @forelse ($files as $file)
                            <flux:table.row :key="$file->id">
                                <flux:table.cell class="flex items-center gap-3">
                                    <flux:icon.document class="size-4 text-zinc-400" />
                                    <flux:text size="sm" class="font-medium truncate max-w-[200px]">{{ $file->original_name }}</flux:text>
                                </flux:table.cell>
                                <flux:table.cell><flux:text size="xs">{{ number_format($file->size / 1024, 1) }} KB</flux:text></flux:table.cell>
                                <flux:table.cell><flux:text size="xs">{{ $file->created_at->diffForHumans() }}</flux:text></flux:table.cell>
                                {{-- <flux:table.cell class="flex justify-end"> --}}
                                    {{-- <flux:button variant="ghost" size="sm" icon="arrow-down-tray" /> --}}
                                {{-- </flux:table.cell> --}}
                            </flux:table.row>
                        @empty
                            <flux:table.row>
                                <flux:table.cell colspan="4" class="py-12 text-center text-zinc-500">No files found.</flux:table.cell>
                            </flux:table.row>
                        @endforelse
                    </flux:table.rows>
                </flux:table>
            </div>
        </section>
    @endif
</div>