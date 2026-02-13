<?php

namespace App\Models;

use Illuminate\Database\Eloquent\Model;
use Illuminate\Database\Eloquent\Relations\BelongsTo;
use Illuminate\Database\Eloquent\Relations\HasMany;
use Illuminate\Support\Facades\Storage;
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

    public function files(): HasMany
    {
        return $this->hasMany(DataFile::class);
    }

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

    protected static function booted()
    {
        static::deleting(function ($data) {
            // Delete all associated files
            // We iterate so that the DataFile's deleting hook is also triggered
            $data->files()->get()->each->delete();
            
            // If the storage_path is a directory (for documents), you might want to clean it
            if ($data->type === 'document') {
                Storage::disk(config('filesystems.default'))->deleteDirectory($data->storage_path);
            }
        });
    }
}
