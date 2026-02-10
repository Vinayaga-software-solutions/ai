<?php

use Livewire\Component;
use App\Models\Project;
use App\Models\DataCollection;
use Livewire\WithPagination;

new class extends Component {
    use WithPagination;

    public Project $project;

    public function mount(Project $project)
    {
        $this->authorize('view', $project);
        // Load creator/updater info only
        $this->project = $project->load(['creator', 'updater']);
    }

    public function delete()
    {
        $this->authorize('delete', $this->project);
        $this->project->delete();
        Flux::toast('Project deleted.');
        return $this->redirect('/project', navigate: true);
    }

    public function with(): array
    {
        return [
            // Paginate the relationship specifically for this project
            'dataCollections' => $this->project->dataCollections()
                ->latest()
                ->paginate(5),
        ];
    }
}; ?>

<div class="space-y-8">
    {{-- Header Section --}}
    <div class="flex items-start justify-between">
        <div class="flex items-center gap-4">
            <div class="p-3 bg-indigo-50 dark:bg-indigo-900/30 rounded-xl">
                <flux:icon.folder class="size-8 text-indigo-600 dark:text-indigo-400" />
            </div>
            <div>
                <flux:heading size="xl" level="1">{{ $project->name }}</flux:heading>
                <div class="flex items-center gap-2 mt-1">
                    <flux:badge size="sm" color="zinc" inset="top bottom">Project ID: #{{ $project->id }}</flux:badge>
                    <flux:text size="sm" class="text-zinc-500">Created {{ $project->created_at->diffForHumans() }}</flux:text>
                </div>
            </div>
        </div>

        <div class="flex items-center gap-2">
            <flux:button href="/project/{{ $project->id }}/edit" icon="pencil-square" variant="ghost" wire:navigate>Edit</flux:button>
            
            <flux:dropdown>
                <flux:button variant="ghost" icon="ellipsis-horizontal" inset="top bottom" />
                <flux:menu>
                    <flux:menu.item icon="trash" variant="danger" wire:click="delete" wire:confirm="Delete this project and all associated data?">
                        Delete Project
                    </flux:menu.item>
                </flux:menu>
            </flux:dropdown>
        </div>
    </div>

    {{-- Stats Cards --}}
    <div class="grid grid-cols-1 md:grid-cols-3 gap-4">
        <div class="p-4 bg-white dark:bg-zinc-900 border border-zinc-200 dark:border-zinc-800 rounded-xl">
            <flux:label>Total Data Collections</flux:label>
            <flux:heading size="lg" class="mt-1">{{ $project->dataCollections()->count() }}</flux:heading>
        </div>
        <div class="p-4 bg-white dark:bg-zinc-900 border border-zinc-200 dark:border-zinc-800 rounded-xl md:col-span-2">
            <flux:label>Project Description</flux:label>
            <flux:text class="block mt-1 truncate-2-lines">{{ $project->description ?: 'No description provided.' }}</flux:text>
        </div>
    </div>

    <flux:separator variant="subtle" />

    {{-- Data Collections List --}}
    <div class="space-y-4">
        <div class="flex items-center justify-between">
            <div>
                <flux:heading size="lg">Data Collections</flux:heading>
                <flux:subheading>Information linked to this specific project.</flux:subheading>
            </div>
            <flux:button href="/datacollection/create?project_id={{ $project->id }}" variant="primary" icon="plus" wire:navigate>
                Add Data Collection
            </flux:button>
        </div>

        <div class="bg-white dark:bg-zinc-900 border border-zinc-200 dark:border-zinc-800 rounded-xl overflow-hidden">
            {{-- Added :paginate attribute --}}
            <flux:table :paginate="$dataCollections">
                <flux:table.columns>
                    {{-- Added padding class to the column header --}}
                    <flux:table.column class="pl-16">Name</flux:table.column>
                    <flux:table.column>Description</flux:table.column>
                    <flux:table.column>Date Created</flux:table.column>
                </flux:table.columns>

                <flux:table.rows>
                    @forelse ($dataCollections as $data)
                        <flux:table.row :key="$data->id">
                            {{-- Added padding class to the cell --}}
                            <flux:table.cell class="pl-16">
                                <flux:link href="/datacollection/{{ $data->id }}/detail" class="font-medium text-indigo-600 dark:text-indigo-400" wire:navigate>
                                    {{ $data->name }}
                                </flux:link>
                            </flux:table.cell>
                            <flux:table.cell class="text-zinc-500">
                                {{ Str::limit($data->description, 60) }}
                            </flux:table.cell>
                            <flux:table.cell class="text-zinc-500 text-sm">
                                {{ $data->created_at->format('M d, Y') }}
                            </flux:table.cell>
                        </flux:table.row>
                    @empty
                        <flux:table.row>
                            <flux:table.cell colspan="3" class="py-10 text-center text-zinc-500 italic">
                                No data entries found for this project.
                            </flux:table.cell>
                        </flux:table.row>
                    @endforelse
                </flux:table.rows>
            </flux:table>
        </div>
    </div>

    <div class="pt-4">
        <flux:button href="/project" variant="ghost" icon="arrow-left" wire:navigate>Back to All Projects</flux:button>
    </div>
</div>