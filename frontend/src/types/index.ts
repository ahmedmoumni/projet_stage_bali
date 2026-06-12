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
  register: (data: RegisterRequest) => Promise<void>;
}

// Document Upload Types
export type FileType = 'pdf_native' | 'pdf_scanned' | 'csv' | 'excel';
export type RoutingType = 'rejected' | 'pipeline1' | 'pipeline2_direct' | 'ocr_then_pipeline1';
export type Visibility = 'public' | 'private';

export interface UploadResponse {
  file_type: FileType;
  routing: RoutingType;
  pages: number;
  text_preview: string;
  log: string[];
  document_id?: number;
  visibility?: Visibility;
  reason?: string;
}

export interface DocumentLog {
  id: number;
  filename: string;
  file_type: string;
  routing: string;
  pages: number;
  rules_extracted: number;
  facts_extracted: number;
  processed_at: string;
}

export interface DocumentListResponse {
  data: DocumentLog[];
}

export interface DocumentDetailResponse {
  data: DocumentLog;
}

export interface UploadRequest {
  file: File;
  visibility?: Visibility;
}
