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

    Route::livewire('/datacollection', 'pages::data-collection.list');
    Route::livewire('/datacollection/create', 'pages::data-collection.create');
    Route::livewire('/datacollection/{dataCollection}/edit', 'pages::data-collection.edit');
    Route::livewire('/datacollection/{dataCollection}/detail', 'pages::data-collection.view');

    Route::livewire('/data', 'pages::data.list');
    Route::livewire('/data/create', 'pages::data.create');
    Route::livewire('/data/{data}/edit', 'pages::data.edit');
    Route::livewire('/data/{data}/detail', 'pages::data.view');
    
require __DIR__.'/settings.php';
