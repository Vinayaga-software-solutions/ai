<?php

use Illuminate\Database\Migrations\Migration;
use Illuminate\Database\Schema\Blueprint;
use Illuminate\Support\Facades\Schema;

return new class extends Migration
{
    /**
     * Run the migrations.
     */
    public function up(): void
    {
        Schema::create('data_files', function (Blueprint $table) {
            $table->id();
            $table->foreignId('data_id')->constrained()->onDelete('cascade');
            $table->string('original_name');
            $table->string('storage_path');
            $table->string('mime_type')->nullable(); // Add this
            $table->unsignedBigInteger('size')->nullable(); // Add this
            $table->timestamps();
        });
    }

    /**
     * Reverse the migrations.
     */
    public function down(): void
    {
        Schema::dropIfExists('data_files');
    }
};
