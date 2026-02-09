<?php

use Illuminate\Support\Facades\Route;

Route::get('/', function () {
    return view('welcome');
})->name('home');

Route::view('dashboard', 'dashboard')
    ->middleware(['auth', 'verified'])
    ->name('dashboard');

    Route::livewire('/project/create', 'pages::project.create');
    Route::livewire('/project', 'pages::project.list');
    Route::livewire('/project/{project}/detail', 'pages::project.view');
    Route::livewire('/project/{project}/edit', 'pages::project.edit');
require __DIR__.'/settings.php';
