<?php

namespace App\Console\Commands;

use Illuminate\Console\Command;
use Illuminate\Support\Facades\DB;

class CleanDatabase extends Command
{
    protected $signature = 'db:clean {--force : Skip confirmation}';

    protected $description = 'Clean database: delete all rules, facts, and pending_review items (keeps users and accounts)';

    public function handle()
    {
        if (!$this->option('force')) {
            $this->warn('⚠️  This will delete:');
            $this->line('  • All knowledge rules');
            $this->line('  • All knowledge facts');
            $this->line('  • All fact values');
            $this->line('  • All document logs');
            $this->line('  • All rule conditions and actions');
            $this->newLine();

            if (!$this->confirm('Continue?')) {
                $this->info('Cancelled.');
                return 1;
            }
        }

        try {
            $this->info('🗑️  Cleaning database...');

            // Disable foreign key checks
            DB::statement('SET FOREIGN_KEY_CHECKS=0');

            // Delete in correct order
            DB::table('rule_action_facts')->truncate();
            $this->info('✓ Deleted rule action facts');

            DB::table('rule_condition_facts')->truncate();
            $this->info('✓ Deleted rule condition facts');

            DB::table('fact_values')->truncate();
            $this->info('✓ Deleted fact values');

            DB::table('knowledge_facts')->truncate();
            $this->info('✓ Deleted knowledge facts');

            DB::table('knowledge_rules')->truncate();
            $this->info('✓ Deleted knowledge rules');

            DB::table('document_logs')->truncate();
            $this->info('✓ Deleted document logs');

            // Re-enable foreign key checks
            DB::statement('SET FOREIGN_KEY_CHECKS=1');

            $this->info('✅ Database cleaned successfully!');
            $this->info('Users and accounts are preserved.');

            return 0;
        } catch (\Exception $e) {
            DB::rollBack();
            $this->error('❌ Error: ' . $e->getMessage());
            return 1;
        }
    }
}
