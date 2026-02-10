<?php

use Livewire\Component;
use App\Models\DataCollection;
use Illuminate\Validation\Rule;

new class extends Component
{
    public DataCollection $dataCollection;
    public string $name = '';
    public string $description = '';

    public function mount(DataCollection $dataCollection)
    {
        $this->authorize('update', $dataCollection);
        $this->dataCollection = $dataCollection;
        $this->name = $dataCollection->name;
        $this->description = $dataCollection->description;
    }

    public function save()
    {
        $this->authorize('update', $this->dataCollection);
        $validated = $this->validate([
            'name' => [
                'required',
                'max:255',
                Rule::unique('data_collections', 'name')->where(fn ($query) => 
                    $query->where('created_by', auth()->id())->where('id', '!=', $this->dataCollection->id)
                ),
            ],
            'description' => 'max:1000',
        ]);

        $this->dataCollection->update([
            'name' => $validated['name'],
            'description' => $validated['description'] ?? '',
            'updated_by' => auth()->id(), // Keeps track of who last edited
        ]);

        Flux::toast('Data Collection updated successfully.');

        return $this->redirect('/datacollection', navigate: true);
    }
};
?>

<div class="max-w-lg mx-auto py-10">
    <flux:heading size="xl" level="1">Edit Data Collection</flux:heading>
    <flux:subheading>Update the details for "{{ $dataCollection->name }}".</flux:subheading>

    <div class="mt-6">
        <form wire:submit="save" class="space-y-6">
            <flux:input 
                wire:model="name" 
                label="Data Collection Name" 
                required 
            />

            <flux:textarea 
                wire:model="description" 
                label="Description" 
                rows="5" 
            />

            <div class="flex items-center justify-end gap-3">
                <flux:button href="/project" variant="ghost" wire:navigate>
                    Cancel
                </flux:button>
                
                <flux:button type="submit" variant="primary">
                    Update Data Collection
                </flux:button>
            </div>
        </form>
    </div>
</div>