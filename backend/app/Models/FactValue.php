<?php

namespace App\Models;

use Illuminate\Database\Eloquent\Factories\HasFactory;
use Illuminate\Database\Eloquent\Model;

class FactValue extends Model
{
    use HasFactory;

    protected $table = 'fact_values';

    protected $fillable = [
        'parent_type',
        'parent_id',
        'value_type',
        'value_continuous',
        'value_categorical',
        'unit',
    ];

    protected $casts = [
        'value_continuous' => 'float',
        'created_at' => 'datetime',
        'updated_at' => 'datetime',
    ];

    /**
     * Get the parent fact (condition, action, or knowledge fact)
     * Returns the polymorphic parent based on parent_type
     */
    public function getParent()
    {
        return match ($this->parent_type) {
            'condition_fact' => RuleConditionFact::find($this->parent_id),
            'action_fact' => RuleActionFact::find($this->parent_id),
            'knowledge_fact' => KnowledgeFact::find($this->parent_id),
            default => null,
        };
    }

    /**
     * Get the display value (continuous or categorical)
     */
    public function getValue()
    {
        return $this->value_type === 'continuous'
            ? $this->value_continuous
            : $this->value_categorical;
    }

    /**
     * Get formatted value with unit if available
     */
    public function getFormattedValue()
    {
        $value = $this->getValue();
        return $this->unit ? "{$value} {$this->unit}" : $value;
    }
}
