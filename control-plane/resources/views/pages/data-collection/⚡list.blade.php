<?php

use Livewire\Component;
use App\Models\DataCollection;
use Livewire\WithPagination;
use App\Models\Project;
use Flux\Flux;

new class extends Component
{
    use WithPagination;

    public string $search = '';

    public function updatedSearch()
    {
        $this->resetPage();
    }

    public function delete($id)
    {
        $data = DataCollection::findOrFail($id);
        $this->authorize('delete', $data);

        $data->delete();
        
        Flux::toast('Data collection deleted successfully.');
    }

    public function with(): array
    {
        return [
            'collections' => DataCollection::query()
                ->with('project')
                ->when($this->search, function ($query) {
                    $query->where('name', 'like', '%' . $this->search . '%')
                          ->orWhere('description', 'like', '%' . $this->search . '%');
                })
                ->latest()
                ->paginate(10),
        ];
    }
};
?>

<div class="space-y-6">
    {{-- Header Section --}}
    <div class="flex items-center justify-between">
        <div>
            <flux:heading size="xl" level="1">Data Collections</flux:heading>
            <flux:subheading>Manage logical groupings of information for your projects.</flux:subheading>
        </div>
        <flux:button href="/datacollection/create" variant="primary" icon="plus" wire:navigate>
            Add Collection
        </flux:button>
    </div>

    <flux:separator variant="subtle" />

    {{-- Search Bar --}}
    <div class="flex flex-col md:flex-row gap-4">
        <flux:input wire:model.live.debounce.300ms="search" view="search" placeholder="Search collections..." class="flex-1" />
    </div>

    {{-- Table Section --}}
    <div class="bg-white dark:bg-zinc-900 border border-zinc-200 dark:border-zinc-800 rounded-xl overflow-hidden">
        <flux:table :paginate="$collections">
            <flux:table.columns>
                <flux:table.column>
                    <div class="pl-4">Name</div>
                </flux:table.column>
                <flux:table.column>Project</flux:table.column>
                <flux:table.column>Created</flux:table.column>
                <flux:table.column align="end"></flux:table.column>
            </flux:table.columns>

            <flux:table.rows>
                @forelse ($collections as $item)
                    <flux:table.row :key="$item->id">
                        {{-- Name & Description --}}
                        <flux:table.cell>
                            <div class="pl-4">
                                <flux:link href="/datacollection/{{ $item->id }}/detail" class="font-medium text-zinc-800 dark:text-white" wire:navigate>
                                    {{ $item->name }}
                                </flux:link>
                                <flux:text size="xs" class="block text-zinc-500 mt-1">{{ Str::limit($item->description, 60) }}</flux:text>
                            </div>
                        </flux:table.cell>

                        {{-- Parent Project Badge --}}
                        <flux:table.cell>
                            <flux:badge size="sm" color="zinc" inset="top bottom">
                                <flux:link href="/project/{{ $item->project_id }}/detail" class="text-zinc-600 dark:text-zinc-400 hover:text-indigo-600" wire:navigate>
                                    {{ $item->project->name }}
                                </flux:link>
                            </flux:badge>
                        </flux:table.cell>

                        {{-- Date --}}
                        <flux:table.cell class="text-zinc-500 text-sm">
                            {{ $item->created_at->format('M d, Y') }}
                        </flux:table.cell>

                        {{-- Actions --}}
                        <flux:table.cell align="end">
                            <div class="flex justify-end gap-2 pr-2">
                                <flux:button variant="ghost" size="sm" icon="pencil-square" href="/datacollection/{{ $item->id }}/edit" wire:navigate />
                                <flux:button variant="ghost" size="sm" icon="trash" wire:click="delete({{ $item->id }})" wire:confirm="Delete this collection and all linked data?" class="text-red-500 hover:text-red-600" />
                            </div>
                        </flux:table.cell>
                    </flux:table.row>
                @empty
                    <flux:table.row>
                        <flux:table.cell colspan="4" class="py-20">
                            <div class="text-center">
                                <flux:icon.document-duplicate class="mx-auto size-12 text-zinc-400" />
                                <flux:heading class="mt-4">No collections found</flux:heading>
                                <flux:subheading>Start by creating a collection to organize your data sources.</flux:subheading>
                            </div>
                        </flux:table.cell>
                    </flux:table.row>
                @endforelse
            </flux:table.rows>
        </flux:table>
    </div>
</div>