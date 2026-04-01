export interface User {
  id: number
  name: string
  surname: string
  email: string
  created_at: string
}

export interface LoginRequest {
  email: string
  password: string
}

export interface RegisterRequest {
  name: string
  surname: string
  email: string
  password: string
}

export interface TokenResponse {
  access_token: string
  token_type: string
}
