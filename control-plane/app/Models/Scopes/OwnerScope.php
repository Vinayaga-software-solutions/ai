<?php

namespace App\Models\Scopes;

use Illuminate\Database\Eloquent\Builder;
use Illuminate\Database\Eloquent\Model;
use Illuminate\Database\Eloquent\Scope;
use Illuminate\Support\Facades\Auth;

class OwnerScope implements Scope
{
    public function apply(Builder $builder, Model $model): void
    {
        // Automatically add "where created_by = current_user_id" to all queries
        if (Auth::check()) {
            $builder->where('created_by', Auth::id());
        }
    }
}