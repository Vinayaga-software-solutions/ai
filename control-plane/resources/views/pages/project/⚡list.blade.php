<?php

use Livewire\Component;
use App\Models\Project;
use Livewire\WithPagination;

new class extends Component
{
    use WithPagination;

    public function with(): array
    {
        $this->authorize('viewAny', Project::class);
        return [
            'projects' => Project::where('created_by', auth()->id())->with(['creator', 'updater'])->latest()->paginate(10),
        ];
    }
};
?>

<div>
    @if (session()->has('message'))
        <div style="color: green; margin-bottom: 10px;">{{ session('message') }}</div>
    @endif
<div class="space-y-6">
    {{-- Header Section --}}
    <div class="flex items-center justify-between">
        <div>
            <flux:heading size="xl" level="1">Projects</flux:heading>
            <flux:subheading>Manage and view your team's ongoing projects.</flux:subheading>
        </div>
        <flux:button href="/project/create" variant="primary" icon="plus" wire:navigate>
            Create Project
        </flux:button>
    </div>

    <flux:separator variant="subtle" />

    {{-- Project Table --}}
    <flux:table :paginate="$projects">
        <flux:table.columns>
            <flux:table.column>Name</flux:table.column>
            <flux:table.column>Description</flux:table.column>
            <flux:table.column>Created By</flux:table.column>
            <flux:table.column>Updated By</flux:table.column>
            <flux:table.column align="end">Actions</flux:table.column>
        </flux:table.columns>

        <flux:table.rows>
            @foreach ($projects as $project)
                <flux:table.row :key="$project->id">
                    <flux:table.cell>
                        {{-- Hyperlink to View Page --}}
                        <flux:link href="/project/{{ $project->id }}/detail" variant="ghost" wire:navigate class="font-medium text-zinc-800 dark:text-white">
                            {{ $project->name }}
                        </flux:link>
                    </flux:table.cell>

                    <flux:table.cell class="text-zinc-500">
                        {{ Str::limit($project->description, 60) }}
                    </flux:table.cell>

                    <flux:table.cell>
                        <flux:badge size="sm" inset="top bottom">{{ $project->creator->name ?? 'System' }}</flux:badge>
                    </flux:table.cell>

                    <flux:table.cell>
                        <flux:text size="sm">{{ $project->updater->name ?? 'System' }}</flux:text>
                    </flux:table.cell>

                    {{-- <flux:table.cell align="end">
                        <div class="flex justify-end gap-2">
                            <flux:button 
                                variant="ghost" 
                                size="sm" 
                                icon="pencil-square" 
                                href="{{ route('projects.edit', $project) }}" 
                                wire:navigate 
                            />
                            <flux:button 
                                variant="ghost" 
                                size="sm" 
                                icon="trash" 
                                wire:click="delete({{ $project->id }})" 
                                wire:confirm="Are you sure you want to delete this project?" 
                                class="text-red-500 hover:text-red-600"
                            />
                        </div>
                    </flux:table.cell> --}}
                </flux:table.row>
            @endforeach
        </flux:table.rows>
    </flux:table>
</div>