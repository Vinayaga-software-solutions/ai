<?php

use Livewire\Component;
use App\Models\DataCollection;

new class extends Component {
    public DataCollection $dataCollection;

    public function mount(DataCollection $dataCollection)
    {
        $this->authorize('view', $dataCollection);
        // Load relationships to avoid the creator/updater name error
        $this->dataCollection = $dataCollection->load(['creator', 'updater']);
    }

    public function delete()
    {
        $this->authorize('delete', $this->dataCollection);
        $this->dataCollection->delete();
        Flux::toast('Data Collection deleted.');
        return $this->redirect('/datacollection', navigate: true);
    }
}; ?>

<div class="max-w-2xl mx-auto py-10">
    <div class="flex items-center justify-between mb-8">
        <div>
            <flux:heading size="xl">{{ $dataCollection->title }}</flux:heading>
            <flux:subheading>Data Collection Details & Overview</flux:subheading>
        </div>

        <flux:dropdown>
            <flux:button variant="ghost" icon="cog-6-tooth" inset="top bottom" />

            <flux:menu>
                <flux:menu.item 
                    icon="pencil-square" 
                    href="/datacollection/{{ $dataCollection->id }}/edit" 
                    wire:navigate
                >
                    Edit Data Collection
                </flux:menu.item>

                <flux:menu.separator />

                {{-- Using wire:click instead of a link for delete --}}
                <flux:menu.item 
                    icon="trash" 
                    variant="danger"
                    wire:click="delete"
                    wire:confirm="Are you sure you want to delete this data collection?"
                >
                    Delete Data Collection
                </flux:menu.item>
            </flux:menu> {{-- This was missing! --}}
        </flux:dropdown>
    </div>

    <flux:separator variant="subtle" />

    <div class="mt-8 space-y-6">
        <div>
            <flux:label>Description</flux:label>
            <p class="mt-2 text-zinc-800 dark:text-zinc-200 leading-relaxed">
                {{ $dataCollection->description ?: 'No description provided.' }}
            </p>
        </div>

        <div>
            <flux:label>Project</flux:label>
            <p class="mt-2 text-zinc-800 dark:text-zinc-200 leading-relaxed">
                <flux:link href="/project/{{ $dataCollection->project_id }}/detail" wire:navigate>
                    {{ $dataCollection->project->name }}
                </flux:link>
            </p>
        </div>

        <div class="grid grid-cols-2 gap-6 pt-6 border-t border-zinc-100 dark:border-zinc-800">
            <div>
                <flux:label>Created By</flux:label>
                <flux:text class="block mt-1">{{ $dataCollection->creator->name ?? 'N/A' }}</flux:text>
            </div>
            <div>
                <flux:label>Last Updated By</flux:label>
                <flux:text class="block mt-1">{{ $dataCollection->updater->name ?? 'N/A' }}</flux:text>
            </div>
            <div>
                <flux:label>Created At</flux:label>
                <flux:text class="block mt-1">{{ $dataCollection->created_at->format('M d, Y') }}</flux:text>
            </div>
        </div>
    </div>

    <div class="mt-10">
        <flux:button href="/datacollection" variant="ghost" icon="arrow-left" wire:navigate>
            Back to Data Collections
        </flux:button>
    </div>
</div>