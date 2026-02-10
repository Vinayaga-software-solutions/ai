<?php

use Livewire\Component;
use App\Models\DataCollection;
use Livewire\WithPagination;
use App\Models\Project;

new class extends Component
{
    use WithPagination;

    public function delete($id)
    {
        $data = DataCollection::findOrFail($id);
        
        // Authorization check
        $this->authorize('delete', $data);

        $data->delete();
        
        Flux::toast('Data entry deleted successfully.');
    }

    public function with(): array
    {
        return [
            // Eager load 'project' to show the project name without extra queries
            'collections' => DataCollection::query()
                ->with('project')
                ->latest()
                ->paginate(10),
        ];
    }
};
?>

<div class="space-y-6">
    <div class="flex items-center justify-between">
        <div>
            <flux:heading size="xl" level="1">Data Collections</flux:heading>
            <flux:subheading>Manage information linked to your projects.</flux:subheading>
        </div>
        <flux:button href="/datacollection/create" variant="primary" icon="plus" wire:navigate>
            Add Data Collection
        </flux:button>
    </div>

    <flux:separator variant="subtle" />

    <flux:table :paginate="$collections">
        <flux:table.columns>
            <flux:table.column>Name</flux:table.column>
            <flux:table.column>Project</flux:table.column>
            <flux:table.column>Description</flux:table.column>
        </flux:table.columns>

        <flux:table.rows>
            @foreach ($collections as $item)
                <flux:table.row :key="$item->id">
                    <flux:table.cell class="font-medium" wire:navigate>
                        <flux:link href="/datacollection/{{ $item->id }}/detail" variant="ghost" wire:navigate class="font-medium text-zinc-800 dark:text-white">
                            {{ $item->name }}
                        </flux:link>
                    </flux:table.cell>

                    <flux:table.cell>
                        {{-- Link to the parent project --}}
                        <flux:badge size="sm" color="zinc" inset="top bottom" wire:navigate>
                            <flux:link href="/project/{{ $item->project_id }}/detail" variant="ghost" wire:navigate class="text-zinc-500 hover:text-zinc-700">
                            {{ $item->project->name }}
                            </flux:link>
                        </flux:badge>
                    </flux:table.cell>

                    <flux:table.cell class="text-zinc-500">
                        {{ Str::limit($item->description, 50) }}
                    </flux:table.cell>
{{-- 
                    <flux:table.cell align="end">
                        <div class="flex justify-end gap-2">
                            <flux:button 
                                variant="ghost" 
                                size="sm" 
                                icon="pencil-square" 
                                href="/datacollection/{{ $item->id }}/edit" 
                                wire:navigate 
                            />
                            <flux:button 
                                variant="ghost" 
                                size="sm" 
                                icon="trash" 
                                wire:click="delete({{ $item->id }})" 
                                wire:confirm="Delete this data entry?" 
                                class="text-red-500 hover:text-red-600"
                            />
                        </div>
                    </flux:table.cell> --}}
                </flux:table.row>
            @endforeach
        </flux:table.rows>
    </flux:table>
</div>