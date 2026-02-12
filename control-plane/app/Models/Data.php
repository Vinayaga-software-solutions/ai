<?php

namespace App\Models;

use Illuminate\Database\Eloquent\Model;
use Illuminate\Database\Eloquent\Relations\BelongsTo;

#[ScopedBy(OwnerScope::class)]
class Data extends Model
{
    protected $fillable = [
        'data_collection_id',
        'name',
        'description',
        'type',
        'connector',
        'connector_config',
        'storage_path',
        'storage_config',
        'created_by',
    ];

    /**
     * Relationship to the Data Collection
     */
    public function dataCollection(): BelongsTo
    {
        return $this->belongsTo(DataCollection::class);
    }

    /**
     * Relationship to the User
     */
    public function creator(): BelongsTo
    {
        return $this->belongsTo(User::class, 'created_by');
    }

    /**
     * Helper to get the formatted GCS URI if it's a document type
     */
    public function getGcsUriAttribute(): ?string
    {
        if ($this->type !== 'document') return null;
        
        return "gs://" . config('services.gcs.bucket') . "/" . $this->storage_path;
    }

    /**
     * Helper to determine which driver to use for processing
     */
    public function getDriver(): string
    {
        return match($this->type) {
            'document' => 'gcs',
            'table'    => 'bigquery', // or 'sql'
            'json'     => 'mongodb',  // or 'firestore'
            default    => 'local',
        };
    }
}
