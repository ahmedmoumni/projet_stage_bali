<?php

use Illuminate\Database\Migrations\Migration;
use Illuminate\Database\Schema\Blueprint;
use Illuminate\Support\Facades\Schema;

return new class extends Migration
{
    public function up(): void
    {
        Schema::create('fact_values', function (Blueprint $table) {
            $table->id();
            $table->enum('parent_type', ['condition_fact', 'action_fact', 'knowledge_fact']);
            $table->unsignedBigInteger('parent_id'); // FK pointing to parent table
            $table->enum('value_type', ['continuous', 'categorical']);
            $table->float('value_continuous')->nullable(); // for continuous values
            $table->string('value_categorical', 255)->nullable(); // for categorical values
            $table->string('unit', 50)->nullable(); // e.g. L, kg, IDR, persons
            $table->timestamps();

            $table->index(['parent_type', 'parent_id']);
            $table->index('value_type');
        });
    }

    public function down(): void
    {
        Schema::dropIfExists('fact_values');
    }
};
