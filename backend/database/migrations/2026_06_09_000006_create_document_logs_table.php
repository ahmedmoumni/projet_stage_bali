<?php

use Illuminate\Database\Migrations\Migration;
use Illuminate\Database\Schema\Blueprint;
use Illuminate\Support\Facades\Schema;

return new class extends Migration
{
    public function up(): void
    {
        Schema::create('document_logs', function (Blueprint $table) {
            $table->id();
            $table->string('filename', 255);
            $table->string('file_type', 50); // pdf_native | pdf_scanned | csv | excel
            $table->string('routing', 50); // rejected | pipeline1 | pipeline2_direct | ocr_then_pipeline1
            $table->integer('pages')->nullable();
            $table->integer('rules_extracted')->default(0);
            $table->integer('facts_extracted')->default(0);
            $table->timestamp('processed_at')->useCurrent();

            $table->index('file_type');
            $table->index('routing');
            $table->index('processed_at');
        });
    }

    public function down(): void
    {
        Schema::dropIfExists('document_logs');
    }
};
