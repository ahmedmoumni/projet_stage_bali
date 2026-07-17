<?php

namespace Database\Seeders;

use App\Models\User;
use Illuminate\Database\Console\Seeds\WithoutModelEvents;
use Illuminate\Database\Seeder;
use Illuminate\Support\Facades\Hash;

class DatabaseSeeder extends Seeder
{
    use WithoutModelEvents;

    /**
     * Seed the application's database.
     */
    public function run(): void
    {
        // Create admin user only if it doesn't exist
        if (!User::where('username', 'admin')->exists()) {
            User::create([
                'username' => 'admin',
                'email' => 'admin@example.com',
                'password' => Hash::make('admin'),
                'role' => 'admin',
            ]);
        }

        // Create test user only if it doesn't exist
        if (!User::where('username', 'test')->exists()) {
            User::create([
                'username' => 'test',
                'email' => 'test@example.com',
                'password' => Hash::make('test'),
                'role' => 'public',
            ]);
        }
    }
}
