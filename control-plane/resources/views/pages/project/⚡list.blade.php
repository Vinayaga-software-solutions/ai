<?php

use Livewire\Component;
use App\Models\Project;
use Livewire\WithPagination;
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
        $project = Project::findOrFail($id);
        $this->authorize('delete', $project);

        $project->delete();
        
        Flux::toast('Project deleted successfully.');
    }

    public function with(): array
    {
        $this->authorize('viewAny', Project::class);

        return [
            'projects' => Project::query()
                ->where('created_by', auth()->id())
                ->when($this->search, function ($query) {
                    $query->where('name', 'like', '%' . $this->search . '%')
                          ->orWhere('description', 'like', '%' . $this->search . '%');
                })
                ->with(['creator', 'updater'])
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
            <flux:heading size="xl" level="1">Projects</flux:heading>
            <flux:subheading>Manage and view your team's ongoing AI projects.</flux:subheading>
        </div>
        <flux:button href="/project/create" variant="primary" icon="plus" wire:navigate>
            Create Project
        </flux:button>
    </div>

    <flux:separator variant="subtle" />

    {{-- Search Bar --}}
    <div class="flex flex-col md:flex-row gap-4">
        <flux:input wire:model.live.debounce.300ms="search" view="search" placeholder="Search projects..." class="flex-1" />
    </div>

    {{-- Project Table --}}
    <div class="bg-white dark:bg-zinc-900 border border-zinc-200 dark:border-zinc-800 rounded-xl overflow-hidden">
        <flux:table :paginate="$projects">
            <flux:table.columns>
                <flux:table.column>
                    <div class="pl-4">Name</div>
                </flux:table.column>
                <flux:table.column>Description</flux:table.column>
                <flux:table.column>Created</flux:table.column>
                <flux:table.column align="end"></flux:table.column>
            </flux:table.columns>

            <flux:table.rows>
                @forelse ($projects as $project)
                    <flux:table.row :key="$project->id">
                        {{-- Name with padding fix --}}
                        <flux:table.cell>
                            <div class="pl-4">
                                <flux:link href="/project/{{ $project->id }}/detail" class="font-medium text-zinc-800 dark:text-white" wire:navigate>
                                    {{ $project->name }}
                                </flux:link>
                            </div>
                        </flux:table.cell>

                        {{-- Description --}}
                        <flux:table.cell class="text-zinc-500">
                            {{ Str::limit($project->description, 80) }}
                        </flux:table.cell>

                        {{-- Date --}}
                        <flux:table.cell class="text-zinc-500 text-sm">
                            {{ $project->created_at->format('M d, Y') }}
                        </flux:table.cell>

                        {{-- Actions --}}
                        <flux:table.cell align="end">
                            <div class="flex justify-end gap-2 pr-2">
                                <flux:button variant="ghost" size="sm" icon="pencil-square" href="/project/{{ $project->id }}/edit" wire:navigate />
                                <flux:button variant="ghost" size="sm" icon="trash" wire:click="delete({{ $project->id }})" wire:confirm="Delete this project? This will remove all associated collections." class="text-red-500 hover:text-red-600" />
                            </div>
                        </flux:table.cell>
                    </flux:table.row>
                @empty
                    <flux:table.row>
                        <flux:table.cell colspan="4" class="py-20">
                            <div class="text-center">
                                <flux:icon.folder-plus class="mx-auto size-12 text-zinc-400" />
                                <flux:heading class="mt-4">No projects found</flux:heading>
                                <flux:subheading>Ready to start? Create your first AI project today.</flux:subheading>
                            </div>
                        </flux:table.cell>
                    </flux:table.row>
                @endforelse
            </flux:table.rows>
        </flux:table>
    </div>
</div>