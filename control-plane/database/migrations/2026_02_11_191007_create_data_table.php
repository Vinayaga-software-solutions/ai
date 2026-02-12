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
    Schema::create('data', function (Blueprint $table) {
            $table->id();
            $table->foreignId('data_collection_id')->constrained();
            $table->string('name');
            $table->text('description')->nullable();
            $table->enum('type', ['document', 'table', 'json']);
            $table->enum('connector', ['Airbyte', 'RudderStack'])->nullable(); // Optional: if using a connector
            $table->json('connector_config')->nullable(); // Connection strings or schema info
            $table->string('storage_path'); // GCS URI, Table Name, or Collection Name
            $table->json('storage_config')->nullable(); // Connection strings or schema info
            $table->foreignId('created_by')->constrained('users');
            $table->timestamps();
    });
    }

    /**
     * Reverse the migrations.
     */
    public function down(): void
    {
        Schema::dropIfExists('data');
    }
};
