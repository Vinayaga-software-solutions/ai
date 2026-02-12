<?php

use Livewire\Component;
use App\Models\Data;
use Flux\Flux;

new class extends Component {
    public Data $data;
    public string $name = '';
    public string $description = '';

    public function mount(Data $data)
    {
        // Eager load the hierarchy for the clickable links
        $this->data = $data->load('dataCollection.project');
        $this->name = $data->name;
        $this->description = $data->description ?? '';
    }

    public function save()
    {
        $validated = $this->validate([
            'name' => [
                'required', 
                'max:255',
                \Illuminate\Validation\Rule::unique('data', 'name')
                    ->where('data_collection_id', $this->data->data_collection_id)
                    ->ignore($this->data->id),
            ],
            'description' => 'nullable|max:2000',
        ]);

        $this->data->update($validated);

        Flux::toast('Data source updated successfully.');

        return $this->redirect('/data', navigate: true);
    }
}; ?>

<div class="max-w-lg mx-auto py-10">
    <flux:heading size="xl" level="1">Edit Data Source</flux:heading>
    <flux:subheading>Update the identifying details. Structural and storage settings are read-only.</flux:subheading>

    <form wire:submit="save" class="mt-6 space-y-6">
        {{-- Clickable Context Breadcrumbs --}}
        <div class="grid grid-cols-2 gap-4 p-4 bg-zinc-50 dark:bg-zinc-900 border border-zinc-200 dark:border-zinc-800 rounded-xl">
            <div>
                <flux:label>Project</flux:label>
                <div class="flex items-center gap-2 mt-1">
                    <flux:icon.folder class="size-4 text-zinc-400" />
                    <flux:link href="/project/{{ $data->dataCollection->project->id }}/detail" size="sm" class="font-medium" wire:navigate>
                        {{ $data->dataCollection->project->name }}
                    </flux:link>
                </div>
            </div>

            <div>
                <flux:label>Collection</flux:label>
                <div class="flex items-center gap-2 mt-1">
                    <flux:icon.document-duplicate class="size-4 text-zinc-400" />
                    <flux:link href="/datacollection/{{ $data->dataCollection->id }}/detail" size="sm" class="font-medium" wire:navigate>
                        {{ $data->dataCollection->name }}
                    </flux:link>
                </div>
            </div>

            <div class="col-span-2 pt-2 border-t border-zinc-200 dark:border-zinc-800">
                <flux:label>Storage Type</flux:label>
                <flux:text size="sm" class="font-medium capitalize">{{ $data->type }}</flux:text>
            </div>
        </div>

        {{-- Editable Fields --}}
        <flux:input 
            wire:model="name" 
            label="Source Name" 
            required 
        />

        <flux:textarea 
            wire:model="description" 
            label="Description" 
            rows="5" 
        />

        <div class="flex justify-end gap-3 pt-4">
            <flux:button variant="ghost" onclick="history.back()">Cancel</flux:button>
            <flux:button type="submit" variant="primary">Save Changes</flux:button>
        </div>
    </form>
</div>