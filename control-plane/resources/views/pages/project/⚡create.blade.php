<?php

use Livewire\Component;
use App\Models\Project;

new class extends Component
{
    public string $name = '';
 
    public string $description = '';
 
    public function save()
    {
        $project = $this->validate([
            'name' => 'required|max:255',
            'description' => 'max:1000',
        ]);
 
        Project::create([
            'name' => $project['name'],
            'description' => $project['description'] ?? '',
            'created_by' => auth()->id(),
            'updated_by' => auth()->id(),
        ]);
    }
};
?>

 <div class="max-w-lg">
    <flux:heading size="xl" level="1">Create Project</flux:heading>
    <flux:subheading>Enter the details below to start a new project.</flux:subheading>

    <div class="mt-6">
        <form wire:submit="save" class="space-y-6">
            {{-- Project Name Input --}}
            <flux:input 
                wire:model="name" 
                label="Project Name" 
                placeholder="e.g. Customer Feedback Analysis" 
                required 
            />

            {{-- Description Textarea --}}
            <flux:textarea 
                wire:model="description" 
                label="Description" 
                placeholder="Describe the project goals..." 
                rows="5" 
            />

            <div class="flex justify-end">
                <flux:button type="submit" variant="primary">
                    Create Project
                </flux:button>
            </div>
        </form>
    </div>
</div>