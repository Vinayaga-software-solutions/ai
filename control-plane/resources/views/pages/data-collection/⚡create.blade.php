<?php

use Livewire\Component;
use App\Models\Project;
use App\Models\DataCollection;
use Illuminate\Validation\Rule;
new class extends Component
{
    public string $name = '';
    public string $description = '';
    public ?int $project_id = null;

    public function mount()
    {
        // Pre-select the first project so it's never null
        $this->project_id = request('project_id') ?? Project::query()->first()?->id;
    }

    public function with(): array
    {
        return [
            'projects' => Project::query()->get(),
        ];
    }

    public function save()
    {
        $project = Project::findOrFail($this->project_id);
        $this->authorize('create', $project);
        $validated = $this->validate([
            'project_id' => 'required|exists:projects,id',
           'name' => [
            'required',
            'max:255',
            // Unique check: Look in data_collections table, name column
            Rule::unique('data_collections', 'name')
                ->where('project_id', $this->project_id), // Scope it to THIS project
        ],
            'description' => 'max:2000',
        ]);

        DataCollection::create([
            'project_id' => $validated['project_id'],
            'name' => $validated['name'],
            'description' => $validated['description'],
            'created_by' => auth()->id(),
            'updated_by' => auth()->id(),
        ]);

        Flux::toast('Data Collection created successfully.');

        return $this->redirect('/datacollection', navigate: true);
    }
};
?>

<div class="max-w-lg">
@if($projects->isEmpty())
        <div class="mt-6 p-8 border border-dashed border-zinc-300 rounded-xl text-center">
            <flux:icon.folder class="mx-auto size-12 text-zinc-400" />
            <flux:heading class="mt-4">No projects found</flux:heading>
            <flux:subheading class="mb-6">You need to create a project before you can add data collections to it.</flux:subheading>
            
            <flux:button href="/project/create" variant="primary" icon="plus" wire:navigate>
                Create Your First Project
            </flux:button>
        </div>
@else
    <flux:heading size="xl" level="1">New Data Entry</flux:heading>
    <flux:subheading>Collect and link new information to an existing project.</flux:subheading>

    <div class="mt-6">
        <form wire:submit="save" class="space-y-6">
            {{-- Project Selection with Autocomplete --}}
            {{-- Ensure wire:model is on the flux:select, not the options --}}
            <flux:select wire:model="project_id" label="Select Project" required>
                @foreach($projects as $project)
                    {{-- Use :value (with a colon) to pass it as an integer --}}
                    <flux:select.option :value="$project->id">
                        {{ $project->name }}
                    </flux:select.option>
                @endforeach
            </flux:select>

            {{-- Data Name --}}
            <flux:input 
                wire:model="name" 
                label="Entry Name" 
                placeholder="e.g. Q1 Market Research" 
                required 
            />

            {{-- description Area --}}
            <flux:textarea 
                wire:model="description" 
                label="Detailed description" 
                placeholder="Enter the findings or data points here..." 
                rows="8" 
            />

            <div class="flex justify-end gap-3">
                <flux:button href="/data" variant="ghost" wire:navigate>Cancel</flux:button>
                <flux:button type="submit" variant="primary">Save</flux:button>
            </div>
        </form>
    </div>
@endif
</div>