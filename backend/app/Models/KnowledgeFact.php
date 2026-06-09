<?php

namespace App\Models;

use Illuminate\Database\Eloquent\Factories\HasFactory;
use Illuminate\Database\Eloquent\Model;
use Illuminate\Database\Eloquent\Relations\HasMany;

class KnowledgeFact extends Model
{
    use HasFactory;

    protected $table = 'knowledge_facts';

    protected $fillable = [
        'source_text',
        'subject',
        'relation',
        'domain',
        'visibility',
        'confidence_score',
        'extraction_method',
        'algorithm_used',
        'status',
    ];

    protected $casts = [
        'confidence_score' => 'float',
        'created_at' => 'datetime',
        'updated_at' => 'datetime',
    ];

    /**
     * Get all fact values for this knowledge fact
     */
    public function factValues(): HasMany
    {
        return $this->hasMany(FactValue::class, 'parent_id')
            ->where('parent_type', 'knowledge_fact');
    }

    /**
     * Get the object (from fact_values) as a formatted string
     */
    public function getObject()
    {
        $values = $this->factValues()->get();
        return $values->map(fn($fv) => $fv->getFormattedValue())->join(', ');
    }

    /**
     * Get full triplet as string: subject - relation - object
     */
    public function getTriplet()
    {
        return "{$this->subject} {$this->relation} {$this->getObject()}";
    }
}
