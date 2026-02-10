<?php

use Livewire\Component;
use App\Models\Project;
use Illuminate\Validation\Rule;

new class extends Component
{
    public Project $project;
    public string $name = '';
    public string $description = '';

    public function mount(Project $project)
    {
        $this->authorize('edit', $project);
        $this->project = $project;
        $this->name = $project->name;
        $this->description = $project->description;
    }

    public function save()
    {
        $this->authorize('edit', $this->project);
        $validated = $this->validate([
            'name' => [
                'required',
                'max:255',
                Rule::unique('projects', 'name')->where(fn ($query) => 
                    $query->where('created_by', auth()->id())->where('id', '!=', $this->project->id)
                ),
            ],
            'description' => 'max:1000',
        ]);

        $this->project->update([
            'name' => $validated['name'],
            'description' => $validated['description'] ?? '',
            'updated_by' => auth()->id(), // Keeps track of who last edited
        ]);

        Flux::toast('Project updated successfully.');

        return $this->redirect('/project', navigate: true);
    }
};
?>

<div class="max-w-lg mx-auto py-10">
    <flux:heading size="xl" level="1">Edit Project</flux:heading>
    <flux:subheading>Update the details for "{{ $project->name }}".</flux:subheading>

    <div class="mt-6">
        <form wire:submit="save" class="space-y-6">
            <flux:input 
                wire:model="name" 
                label="Project Name" 
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
                    Update Project
                </flux:button>
            </div>
        </form>
    </div>
</div>