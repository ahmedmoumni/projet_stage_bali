export type UserRole = 'admin' | 'public';

export interface User {
  id: number;
  username: string;
  role: UserRole;
  email: string;
  adresse: string;
  numero: string;
}

export interface AuthResponse {
  token: string;
  user: User;
}

export interface LoginRequest {
  username: string;
  password: string;
}

export interface RegisterRequest {
  username: string;
  email: string;
  password: string;
  age: number;
  adresse: string;
  numero: string;
  role?: UserRole;
}

export interface AuthContextType {
  user: User | null;
  token: string | null;
  isAuthenticated: boolean;
  isLoading: boolean;
  login: (username: string, password: string) => Promise<void>;
  logout: () => Promise<void>;
  register?: (data: RegisterRequest) => Promise<void>;
}
