<?php
namespace App\Models;

use App\Services\DataFilePubSubPublisher;
use Illuminate\Database\Eloquent\Model;
use Illuminate\Database\Eloquent\Relations\BelongsTo;
use Illuminate\Support\Facades\Storage;
class DataFile extends Model
{
    protected $fillable = [
        'data_id',
        'original_name',
        'storage_path',
        'mime_type',
        'size',
    ];

    /**
     * Get the parent data source.
     */
    public function data(): BelongsTo
    {
        return $this->belongsTo(Data::class);
    }

    /**
     * Helper to get the human-readable file size.
     */
    public function getReadableSizeAttribute(): string
    {
        $bytes = $this->size;
        $units = ['B', 'KB', 'MB', 'GB'];
        for ($i = 0; $bytes > 1024; $i++) $bytes /= 1024;
        return round($bytes, 2) . ' ' . $units[$i];
    }

    protected static function booted()
    {
        static::created(function ($dataFile) {
            app(DataFilePubSubPublisher::class)->publishFileUploaded($dataFile);
        });

        static::deleting(function ($dataFile) {
            // Remove the actual file from storage
            if (Storage::disk(config('filesystems.default'))->exists($dataFile->storage_path)) {
                Storage::disk(config('filesystems.default'))->delete($dataFile->storage_path);
            }
        });
    }
}
