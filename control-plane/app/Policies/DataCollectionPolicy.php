<?php

namespace App\Policies;

use App\Models\DataCollection;
use App\Models\User;
use Illuminate\Auth\Access\Response;

class DataCollectionPolicy
{
    /**
     * Determine whether the user can view any models.
     */
    public function viewAny(User $user): bool
    {
        return true;
    }

    /**
     * Determine whether the user can view the model.
     */
    public function view(User $user, DataCollection $dataCollection): bool
    {
        return  $user->id === $dataCollection->created_by || $user->id === $dataCollection->project->created_by;
    }

    /**
     * Determine whether the user can create models.
     */
    public function create(User $user, Project $project): bool
    {
        return $user->id === $project->created_by;
    }

    /**
     * Determine whether the user can update the model.
     */
    public function update(User $user, DataCollection $dataCollection): bool
    {
        return $user->id === $dataCollection->project->created_by;
    }

    /**
     * Determine whether the user can delete the model.
     */
    public function delete(User $user, DataCollection $dataCollection): bool
    {
        return  $user->id === $dataCollection->project->created_by;
    }

    /**
     * Determine whether the user can restore the model.
     */
    public function restore(User $user, DataCollection $dataCollection): bool
    {
        return  $user->id === $dataCollection->project->created_by;
    }

    /**
     * Determine whether the user can permanently delete the model.
     */
    public function forceDelete(User $user, DataCollection $dataCollection): bool
    {
        return  $user->id === $dataCollection->project->created_by;
    }
}
