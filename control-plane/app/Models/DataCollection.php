<?php

namespace App\Models;

use Illuminate\Database\Eloquent\Model;
use Illuminate\Database\Eloquent\Relations\HasMany;
class DataCollection extends Model
{
    protected $fillable = ['project_id', 'name', 'description', 'created_by', 'updated_by'];

    public function project() { return $this->belongsTo(Project::class); }
    public function creator() { return $this->belongsTo(User::class, 'created_by'); }
    public function updater() { return $this->belongsTo(User::class, 'updated_by'); }
    public function data(): HasMany
    {
        // 'data_collection_id' is the foreign key in the 'data' table
        return $this->hasMany(Data::class, 'data_collection_id');
    }
}
