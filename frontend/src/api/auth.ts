import { apiClient, setAccessToken } from "./client";

export interface UserDto {
  id: string;
  email: string;
  full_name: string;
  role: "student" | "administrator";
  is_active: boolean;
  is_verified: boolean;
  created_at: string;
  updated_at: string;
}

export interface RegisterRequestDto {
  email: string;
  password: string;
  full_name: string;
}

export interface LoginRequestDto {
  email: string;
  password: string;
}

export interface TokenResponseDto {
  access_token: string;
  token_type: string;
  expires_in: number;
  user: UserDto;
}

export interface RefreshTokenResponseDto {
  access_token: string;
  token_type: string;
  expires_in: number;
}

export async function registerUser(data: RegisterRequestDto): Promise<UserDto> {
  return apiClient<UserDto>("/api/v1/auth/register", {
    method: "POST",
    body: JSON.stringify(data),
    skipAuthRefresh: true,
  });
}

export async function loginUser(data: LoginRequestDto): Promise<TokenResponseDto> {
  const res = await apiClient<TokenResponseDto>("/api/v1/auth/login", {
    method: "POST",
    body: JSON.stringify(data),
    skipAuthRefresh: true,
  });
  setAccessToken(res.access_token);
  return res;
}

export async function refreshAccessToken(): Promise<RefreshTokenResponseDto> {
  const res = await apiClient<RefreshTokenResponseDto>("/api/v1/auth/refresh", {
    method: "POST",
    skipAuthRefresh: true,
  });
  setAccessToken(res.access_token);
  return res;
}

export async function fetchCurrentUser(): Promise<UserDto> {
  return apiClient<UserDto>("/api/v1/auth/me");
}

export async function logoutUser(): Promise<void> {
  try {
    await apiClient<{ message: string }>("/api/v1/auth/logout", {
      method: "POST",
      skipAuthRefresh: true,
    });
  } finally {
    setAccessToken(null);
  }
}
