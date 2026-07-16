<?php
require_once __DIR__.'/vendor/autoload.php';

$app = require_once __DIR__.'/bootstrap/app.php';
$kernel = $app->make(\Illuminate\Contracts\Http\Kernel::class);

$app->make('db');
$app->make('auth');

use App\Models\User;

// Check if admin user exists
$admin = User::where('username', 'admin')->first();
if (!$admin) {
    $admin = User::create([
        'username' => 'admin',
        'email' => 'admin@example.com',
        'password' => bcrypt('password123'),
        'role' => 'admin',
        'age' => 30,
        'adresse' => '123 Main St',
        'numero' => '+1234567890'
    ]);
    echo "Admin user created: " . $admin->id . "\n";
} else {
    echo "Admin user already exists: " . $admin->id . "\n";
}

// Generate token
$token = $admin->createToken('auth_token')->plainTextToken;
echo "Token: " . $token . "\n";
?>
