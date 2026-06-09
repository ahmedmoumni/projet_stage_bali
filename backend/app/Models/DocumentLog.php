<?php

namespace App\Models;

use Illuminate\Database\Eloquent\Factories\HasFactory;
use Illuminate\Database\Eloquent\Model;

class DocumentLog extends Model
{
    use HasFactory;

    protected $table = 'document_logs';

    public $timestamps = false;

    protected $fillable = [
        'filename',
        'file_type',
        'routing',
        'pages',
        'rules_extracted',
        'facts_extracted',
        'processed_at',
    ];

    protected $casts = [
        'processed_at' => 'datetime',
    ];
}
