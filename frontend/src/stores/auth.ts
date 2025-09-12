import { defineStore } from 'pinia';
import { login, register, forgotPassword, LoginCredentials, RegisterData, ForgotPasswordData } from '../services/authService';
import { checkAbacPermission, CheckPermissionRequest } from '../services/apiService';
import router from '../router'; // Import the router for redirection

interface AuthState {
  token: string | null;
  user: any | null; // You might want to define a more specific User type
  permissionCache: Map<string, boolean>;
}

export const useAuthStore = defineStore('auth', {
  state: (): AuthState => ({
    token: localStorage.getItem('token') || null,
    user: JSON.parse(localStorage.getItem('user') || 'null') as any | null,
    permissionCache: new Map<string, boolean>(),
  }),
  getters: {
    isAuthenticated: (state: AuthState) => !!state.token,
  },
  actions: {
    setToken(token: string | null) {
      const store = this as any;
      store.token = token;
      if (token) {
        localStorage.setItem('token', token);
      } else {
        localStorage.removeItem('token');
      }
    },
    setUser(user: any | null) {
      const store = this as any;
      store.user = user;

      if (user) {
        localStorage.setItem('user', JSON.stringify(user));
      } else {
        localStorage.removeItem('user');
      }
    },
    async login(credentials: LoginCredentials): Promise<void> { // Specify return type as Promise<void>
      return new Promise<void>(async (resolve, reject) => { // Return a new Promise
        try {
          const data = await login(credentials);
          // console.log('User data received from login API:', data.user); // Log user data
          this.setToken(data.access_token); // Corrected to access_token
          this.setUser(data.user); // Assuming API returns user info
          // Redirect is now handled in the calling component
          // router.push('/upload'); // Removed
          (this as any).permissionCache.clear(); // Clear permission cache on successful login
          resolve(); // Resolve the promise after setting user and token
        } catch (error) {
          // console.error('Login error:', error);
          // Do not clear user/token here, as the component might need to handle the error
          // while keeping the previous state. The calling component should decide whether to log out.
          reject(error); // Reject the promise on error
        }
      });
    },
    async register(data: RegisterData) {
      try {
        // Assuming registration might return a token or just a success message
        const response = await register(data);
        // Handle response, maybe redirect to login
        // console.log('Registration successful:', response);
        return true; // Indicate success
      } catch (error) {
        // console.error('Registration error:', error);
        throw error; // Re-throw the error for component to handle
      }
    },
    async forgotPassword(data: ForgotPasswordData) {
      try {
        const response = await forgotPassword(data);
        // console.log('Forgot password request successful:', response);
        return true; // Indicate success
      } catch (error) {
        // console.error('Forgot password error:', error);
        throw error; // Re-throw the error for component to handle
      }
    },
    logout() {
      this.setToken(null);
      this.setUser(null);
      (this as any).permissionCache.clear(); // Clear permission cache on logout
      // Redirect to login page after logout
      router.push('/login');
    },
    async can(action: string, resource_type: string, resource_id?: string): Promise<boolean> {
      // HACK: Using 'this as any' to bypass TypeScript context issues, mirroring other actions in this file.
      const store = this as any;

      if (!store.token) {
        return false;
      }

      const cacheKey = `${action}-${resource_type}-${resource_id || ''}`;
      if (store.permissionCache.has(cacheKey)) {
        return store.permissionCache.get(cacheKey) as boolean;
      }

      try {
        const request: CheckPermissionRequest = { action, resource_type, resource_id };
        const response = await checkAbacPermission(request);
        store.permissionCache.set(cacheKey, response.allowed);
        return response.allowed;
      } catch (error) {
        console.error(`Permission check failed for ${cacheKey}:`, error);
        // Default to false in case of an error
        store.permissionCache.set(cacheKey, false);
        return false;
      }
    },
  },
});