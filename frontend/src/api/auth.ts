import client from './client'
import type { LoginRequest, RegisterRequest, TokenResponse, User } from '../types/auth'

export const login = (data: LoginRequest) =>
  client.post<TokenResponse>('/auth/login', data)

export const register = (data: RegisterRequest) =>
  client.post<User>('/auth/register', data)

export const logout = () =>
  client.post('/auth/logout')

export const getMe = () =>
  client.get<User>('/users/me')
