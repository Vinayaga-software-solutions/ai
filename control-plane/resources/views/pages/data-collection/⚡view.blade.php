<?php

use Livewire\Component;
use App\Models\DataCollection;
use App\Models\Data;
use Flux\Flux;

new class extends Component {
    public DataCollection $dataCollection;
    public string $search = '';

    public function mount(DataCollection $dataCollection)
    {
        $this->authorize('view', $dataCollection);
        
        // Load data sources along with creator/updater
        $this->dataCollection = $dataCollection->load(['creator', 'updater', 'data']);
    }

    /**
     * Get filtered data sources for this collection
     */
    public function getDataSourcesProperty()
    {
        return $this->dataCollection->data()
            ->when($this->search, function ($query) {
                $query->where('name', 'like', '%' . $this->search . '%')
                      ->orWhere('type', 'like', '%' . $this->search . '%');
            })
            ->latest()
            ->get();
    }

    public function delete()
    {
        $this->authorize('delete', $this->dataCollection);
        
        // This will trigger the cascade delete and Model hooks 
        // cleaning up all associated Data records and physical files.
        $this->dataCollection->delete();
        
        Flux::toast('Data Collection and all associated data deleted.');
        
        return $this->redirect('/datacollection', navigate: true);
    }
}; ?>

<div class="max-w-4xl mx-auto py-10 space-y-10">
    {{-- Header Section --}}
    <div class="flex items-center justify-between">
        <div>
            <flux:heading size="xl">{{ $dataCollection->name }}</flux:heading>
            <flux:subheading>Data Collection Details & Overview</flux:subheading>
        </div>

        <div class="flex items-center gap-2">
            <flux:button href="/data/create?data_collection_id={{ $dataCollection->id }}" variant="primary" icon="plus" wire:navigate>
                Add Data Source
            </flux:button>
            
            <flux:dropdown>
                <flux:button variant="ghost" icon="cog-6-tooth" inset="top bottom" />
                <flux:menu>
                    <flux:menu.item icon="pencil-square" href="/datacollection/{{ $dataCollection->id }}/edit" wire:navigate>
                        Edit Collection
                    </flux:menu.item>
                    <flux:menu.separator />
                    <flux:menu.item icon="trash" variant="danger" wire:click="delete" wire:confirm="Are you sure? This will delete all data sources and files in this collection.">
                        Delete Collection
                    </flux:menu.item>
                </flux:menu>
            </flux:dropdown>
        </div>
    </div>

    <flux:separator variant="subtle" />

    {{-- Info Grid --}}
    <div class="grid grid-cols-1 md:grid-cols-3 gap-8">
        <div class="md:col-span-2 space-y-6">
            <div>
                <flux:label>Description</flux:label>
                <p class="mt-2 text-zinc-800 dark:text-zinc-200 leading-relaxed">
                    {{ $dataCollection->description ?: 'No description provided.' }}
                </p>
            </div>

            <div class="grid grid-cols-2 gap-4">
                <div>
                    <flux:label>Project</flux:label>
                    <flux:link class="block mt-1" href="/project/{{ $dataCollection->project_id }}/detail" wire:navigate>
                        {{ $dataCollection->project->name }}
                    </flux:link>
                </div>
                <div>
                    <flux:label>Created At</flux:label>
                    <flux:text class="block mt-1">{{ $dataCollection->created_at->format('M d, Y') }}</flux:text>
                </div>
            </div>
        </div>

        <div class="bg-zinc-50 dark:bg-zinc-900 p-6 rounded-xl border border-zinc-200 dark:border-zinc-800 space-y-4">
            <flux:heading size="sm">Stats</flux:heading>
            <div class="flex justify-between items-center">
                <flux:text size="sm">Data Sources</flux:text>
                <flux:badge size="sm" inset="top bottom">{{ $this->dataSources->count() }}</flux:badge>
            </div>
            <div class="flex justify-between items-center">
                <flux:text size="sm">Created By</flux:text>
                <flux:text size="xs" class="font-medium">{{ $dataCollection->creator->name ?? 'N/A' }}</flux:text>
            </div>
        </div>
    </div>

    {{-- Data Sources List --}}
    <section class="space-y-4">
        <div class="flex items-center justify-between">
            <flux:heading size="md">Data Sources</flux:heading>
            <flux:input wire:model.live.debounce.300ms="search" view="search" placeholder="Search sources..." size="sm" class="max-w-xs" />
        </div>

        <div class="bg-white dark:bg-zinc-900 border border-zinc-200 dark:border-zinc-800 rounded-xl overflow-hidden">
            <flux:table>
                <flux:table.columns>
                    <flux:table.column>Name</flux:table.column>
                    <flux:table.column>Type</flux:table.column>
                    <flux:table.column>Created</flux:table.column>
                    <flux:table.column></flux:table.column>
                </flux:table.columns>

                <flux:table.rows>
                    @forelse ($this->dataSources as $source)
                        <flux:table.row :key="$source->id">
                            <flux:table.cell>
                                <flux:link href="/data/{{ $source->id }}/detail" class="font-medium" wire:navigate>
                                    {{ $source->name }}
                                </flux:link>
                            </flux:table.cell>
                            
                            <flux:table.cell>
                                <flux:badge size="sm" color="zinc" inset="top bottom">{{ ucfirst($source->type) }}</flux:badge>
                            </flux:table.cell>

                            <flux:table.cell class="text-zinc-500 text-xs">
                                {{ $source->created_at->format('M d, Y') }}
                            </flux:table.cell>

                            <flux:table.cell class="flex justify-end">
                                <flux:button variant="ghost" size="sm" icon="chevron-right" href="/data/{{ $source->id }}/detail" wire:navigate />
                            </flux:table.cell>
                        </flux:table.row>
                    @empty
                        <flux:table.row>
                            <flux:table.cell colspan="4" class="py-12 text-center text-zinc-500">
                                No data sources found in this collection.
                            </flux:table.cell>
                        </flux:table.row>
                    @endforelse
                </flux:table.rows>
            </flux:table>
        </div>
    </section>

    <div class="pt-6">
        <flux:button href="/datacollection" variant="ghost" icon="arrow-left" wire:navigate>
            Back to Data Collections
        </flux:button>
    </div>
</div>