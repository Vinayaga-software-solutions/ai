<?php

use Livewire\Component;
use App\Models\Data;
use Livewire\WithPagination;
use Flux\Flux;

new class extends Component {
    use WithPagination;

    public string $search = '';
    public string $typeFilter = '';

    public function updatedSearch()
    {
        $this->resetPage();
    }

    public function with(): array
    {
        return [
            'items' => Data::query()
                ->with(['dataCollection.project'])
                ->when($this->search, function ($query) {
                    $query->where('name', 'like', '%' . $this->search . '%')
                          ->orWhere('description', 'like', '%' . $this->search . '%');
                })
                ->when($this->typeFilter, function ($query) {
                    $query->where('type', $this->typeFilter);
                })
                ->latest()
                ->paginate(10),
        ];
    }
}; ?>

<div class="space-y-6">
    <div class="flex items-center justify-between">
        <div>
            <flux:heading size="xl" level="1">Data Sources</flux:heading>
            <flux:subheading>Manage your ingested information streams.</flux:subheading>
        </div>
        <flux:button href="/data/create" variant="primary" icon="plus" wire:navigate>
            Add Data
        </flux:button>
    </div>

    <flux:separator variant="subtle" />

    <div class="flex flex-col md:flex-row gap-4">
        <flux:input wire:model.live.debounce.300ms="search" view="search" placeholder="Search name or description..." class="flex-1" />
        
        <flux:select wire:model.live="typeFilter" placeholder="All Types" class="w-full md:w-48">
            <flux:select.option value="">All Types</flux:select.option>
            <flux:select.option value="document">Documents</flux:select.option>
            <flux:select.option value="table">Tables</flux:select.option>
            <flux:select.option value="json">JSON</flux:select.option>
        </flux:select>
    </div>

    <div class="bg-white dark:bg-zinc-900 border border-zinc-200 dark:border-zinc-800 rounded-xl overflow-hidden">
        <flux:table :paginate="$items">
            <flux:table.columns>
                <flux:table.column>
                    <div class="pl-4">Name</div>
                </flux:table.column>
                <flux:table.column>Type</flux:table.column>
                <flux:table.column>Collection / Project</flux:table.column>
                <flux:table.column>Added</flux:table.column>
            </flux:table.columns>

            <flux:table.rows>
                @forelse ($items as $item)
                    <flux:table.row :key="$item->id">
                        <flux:table.cell>
                            <div class="pl-4">
                                <flux:link href="/data/{{ $item->id }}/detail" class="font-medium text-zinc-800 dark:text-white" wire:navigate>
                                    {{ $item->name }}
                                </flux:link>
                                <flux:text size="xs" class="block text-zinc-500 mt-1">{{ Str::limit($item->description, 50) }}</flux:text>
                            </div>
                        </flux:table.cell>

                        <flux:table.cell>
                            @php
                                $color = match($item->type) {
                                    'document' => 'indigo',
                                    'table' => 'emerald',
                                    'json' => 'amber',
                                    default => 'zinc'
                                };
                            @endphp
                            <flux:badge :color="$color" size="sm" inset="top bottom">{{ ucfirst($item->type) }}</flux:badge>
                        </flux:table.cell>

                        <flux:table.cell>
                            <div class="flex flex-col">
                                <flux:text size="sm" class="font-medium text-zinc-700 dark:text-zinc-300">{{ $item->dataCollection->name }}</flux:text>
                                <flux:text size="xs" class="text-zinc-500">{{ $item->dataCollection->project->name }}</flux:text>
                            </div>
                        </flux:table.cell>

                        <flux:table.cell class="text-zinc-500 text-sm">
                            {{ $item->created_at->format('M d, Y') }}
                        </flux:table.cell>

                    </flux:table.row>
                @empty
                    <flux:table.row>
                        <flux:table.cell colspan="5" class="py-20">
                            <div class="text-center">
                                <flux:icon.document-duplicate class="mx-auto size-12 text-zinc-400" />
                                <flux:heading class="mt-4">No data sources found</flux:heading>
                                <flux:subheading>Initialize your first data source to get started.</flux:subheading>
                            </div>
                        </flux:table.cell>
                    </flux:table.row>
                @endforelse
            </flux:table.rows>
        </flux:table>
    </div>
</div>