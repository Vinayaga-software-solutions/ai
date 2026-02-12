<?php

use Livewire\Component;
use App\Models\Data;
use Flux\Flux;

new class extends Component {
    public Data $data;

    public function mount(Data $data)
    {
        $this->authorize('view', $data);
        // Load relationships to show parent info
        $this->data = $data->load(['dataCollection.project', 'creator']);
    }

    public function delete()
    {
        $this->authorize('delete', $this->data);
        $this->data->delete();

        Flux::toast('Data source deleted.');
        return $this->redirect('/data', navigate: true);
    }
}; ?>

<div class="space-y-8 max-w-4xl mx-auto py-10">
    {{-- Top Navigation & Actions --}}
    <div class="flex items-center justify-between">
        <flux:button variant="ghost" icon="arrow-left" onclick="history.back()" class="-ml-3">Back</flux:button>
        
        <div class="flex items-center gap-2">
            <flux:button :href="'/data/'.$data->id.'/edit'" variant="ghost" icon="pencil-square" wire:navigate>Edit</flux:button>
            <flux:button variant="ghost" icon="trash" class="text-red-500" wire:click="delete" wire:confirm="Permanently delete this data source?" />
        </div>
    </div>

    {{-- Main Header Section --}}
    <div class="flex items-start gap-5">
        <div class="p-4 bg-zinc-100 dark:bg-zinc-800 rounded-2xl">
            @if($data->type === 'document')
                <flux:icon.document-text class="size-10 text-indigo-600" />
            @elseif($data->type === 'table')
                <flux:icon.table-cells class="size-10 text-emerald-600" />
            @else
                <flux:icon.code-bracket class="size-10 text-amber-600" />
            @endif
        </div>

        <div class="flex-1">
            <div class="flex items-center gap-3">
                <flux:heading size="xl">{{ $data->name }}</flux:heading>
                @php
                    $color = match($data->type) {
                        'document' => 'indigo',
                        'table' => 'emerald',
                        'json' => 'amber',
                        default => 'zinc'
                    };
                @endphp
                <flux:badge :color="$color" size="sm" inset="top bottom">{{ ucfirst($data->type) }}</flux:badge>
            </div>
            <flux:text class="mt-1">{{ $data->description ?: 'No description provided.' }}</flux:text>
        </div>
    </div>

    <flux:separator variant="subtle" />

    {{-- Info Grid --}}
    <div class="grid grid-cols-1 md:grid-cols-2 gap-8">
        {{-- Source Context --}}
        <section class="space-y-4">
            <flux:heading size="md">Context</flux:heading>
            
            <div class="space-y-3">
                <div class="flex justify-between border-b border-zinc-100 dark:border-zinc-800 pb-2">
                    <flux:text size="sm" class="text-zinc-500">Project</flux:text>
                    <flux:link href="/project/{{ $data->dataCollection->project->id }}/detail" size="sm" wire:navigate>
                        {{ $data->dataCollection->project->name }}
                    </flux:link>
                </div>
                <div class="flex justify-between border-b border-zinc-100 dark:border-zinc-800 pb-2">
                    <flux:text size="sm" class="text-zinc-500">Collection</flux:text>
                    <flux:link href="/datacollection/{{ $data->dataCollection->id }}/detail" size="sm" wire:navigate>
                        {{ $data->dataCollection->name }}
                    </flux:link>
                </div>
                <div class="flex justify-between">
                    <flux:text size="sm" class="text-zinc-500">Initialized By</flux:text>
                    <flux:text size="sm" class="font-medium text-zinc-800 dark:text-zinc-200">{{ $data->creator->name }}</flux:text>
                </div>
            </div>
        </section>

        {{-- Technical Storage Details --}}
        <section class="space-y-4">
            <flux:heading size="md">Storage Reference</flux:heading>
            
            <div class="p-4 bg-zinc-50 dark:bg-zinc-900 border border-zinc-200 dark:border-zinc-800 rounded-xl">
                <flux:label>Storage Path</flux:label>
                <div class="mt-2 flex items-center gap-2">
                    <code class="text-xs font-mono text-indigo-600 dark:text-indigo-400 break-all">
                        {{ $data->storage_path }}
                    </code>
                    <flux:button variant="ghost" size="sm" icon="clipboard" onclick="navigator.clipboard.writeText('{{ $data->storage_path }}'); Flux.toast('Path copied!')" />
                </div>
                
                @if($data->type === 'document')
                    <div class="mt-4 flex gap-2">
                        <flux:button size="sm" icon="cloud-arrow-down" variant="subtle">Download from GCS</flux:button>
                    </div>
                @endif
            </div>
        </section>
    </div>

    {{-- Connector Configuration (Optional) --}}
    @if($data->connector)
    <section class="space-y-4">
        <flux:heading size="md">Connector Configuration</flux:heading>
        <div class="p-4 border border-zinc-200 dark:border-zinc-800 rounded-xl">
            <div class="flex items-center gap-2 mb-4">
                <flux:badge color="zinc">{{ $data->connector }}</flux:badge>
                <flux:text size="sm">Active Sync</flux:text>
            </div>
            
            <pre class="text-xs bg-zinc-900 text-zinc-300 p-4 rounded-lg overflow-x-auto"><code>{{ json_encode($data->connector_config, JSON_PRETTY_PRINT) }}</code></pre>
        </div>
    </section>
    @endif
</div>