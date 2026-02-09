<?php

namespace App\Models;

use Illuminate\Database\Eloquent\Model;

class Project extends Model
{
    protected $fillable = ['name', 'description', 'created_by', 'updated_by'];

    public function creator() { return $this->belongsTo(User::class, 'created_by'); }
    public function updater() { return $this->belongsTo(User::class, 'updated_by'); }

    protected static function booted()
    {
        static::addGlobalScope('mine', function ($builder) {
            if (auth()->check()) {
                $builder->where('created_by', auth()->id());
            }
        });
    }
}
