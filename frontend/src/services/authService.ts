import { useAuthStore } from '../stores/auth';

const API_BASE_URL = '/api'; // TODO: Configure this properly, maybe using environment variables

export interface LoginCredentials {
  username?: string;
  email?: string;
  phone?: string;
  password?: string;
}

export interface RegisterData {
  username: string;
  email?: string;
  phone?: string;
  password: string;
  department: string; // Required
  first_name?: string; // Optional
  surname?: string; // Optional
  captcha: string; // Add captcha field
}

export interface ForgotPasswordData {
  email_or_phone: string; // Corrected field name to match backend
}

export interface ResetPasswordData {
  token: string;
  new_password: string;
}

export interface AuthResponse {
  access_token: string; // Corrected to access_token
  token_type: string; // Added token_type based on backend response
  user: any; // TODO: Define a proper user type
}

export interface CaptchaVerifyRequest {
  captcha_id: string;
  captcha_input: string;
}

const handleResponse = async (response: Response): Promise<any> => {
  console.log('API Response Status:', response.status);
  const text = await response.text(); // Read response body as text once
  console.log('API Response Text:', text);

  if (!response.ok) {
    let errorDetail = 'API request failed';
    try {
      const error = JSON.parse(text);
      console.error('API Error Details (parsed):', error);

      if (Array.isArray(error.detail)) {
        // Handle Pydantic validation errors (detail is an array of error objects)
        errorDetail = error.detail.map((err: any) => `${err.loc.join('.')} - ${err.msg}`).join(', ');
      } else {
        // Handle other errors (detail is a string or other structure)
        errorDetail = error.detail || text;
      }

    } catch (e) {
      // If parsing fails, use the raw text
      errorDetail = text;
      console.error('API Error Details (raw text):', text);
    }

    // Add specific handling for 401 Unauthorized
    if (response.status === 401) {
      throw new Error('Unauthorized: Please log in again.');
    }

    // Ensure errorDetail is a string before calling substring
    const displayError = typeof errorDetail === 'string' ? errorDetail : JSON.stringify(errorDetail);
    throw new Error(`API request failed with status ${response.status}: ${displayError.substring(0, 200)}...`);
  }

  try {
    // Attempt to parse text as JSON for success response
    const jsonResponse = JSON.parse(text);
    console.log('API Success Response JSON:', jsonResponse);
    return jsonResponse;
  } catch (e) {
    console.error('API Success Response Text (JSON parse failed):', text);
    throw new Error(`API response was not valid JSON (status ${response.status}): ${text.substring(0, 200)}...`);
  }
};

export const login = async (credentials: LoginCredentials): Promise<AuthResponse> => {
  const response = await fetch(`${API_BASE_URL}/login`, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
    },
    body: JSON.stringify(credentials),
  });
  return handleResponse(response);
};

export const register = async (data: RegisterData): Promise<AuthResponse> => {
  const response = await fetch(`${API_BASE_URL}/register`, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
    },
    body: JSON.stringify(data), // The data object now includes captcha
  });
  return handleResponse(response);
};

export const verifyCaptcha = async (data: CaptchaVerifyRequest): Promise<any> => {
  const response = await fetch(`${API_BASE_URL}/captcha/verify`, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
    },
    body: JSON.stringify(data),
  });
  return handleResponse(response);
};


export const forgotPassword = async (data: ForgotPasswordData): Promise<any> => {
  const response = await fetch(`${API_BASE_URL}/forgot-password`, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
    },
    body: JSON.stringify({ email_or_phone: data.email_or_phone }), // Map frontend field to backend field
  });
  return handleResponse(response);
};

export const resetPassword = async (data: ResetPasswordData): Promise<any> => {
  const response = await fetch(`${API_BASE_URL}/reset-password`, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
    },
    body: JSON.stringify(data),
  });
  return handleResponse(response);
};

export const activateUser = async (token: string): Promise<any> => {
  const response = await fetch(`${API_BASE_URL}/activate?token=${token}`, {
    method: 'GET',
  });
  return handleResponse(response);
};

export const handleThirdPartyAuthCallback = async (token: string): Promise<AuthResponse> => {
  const authStore = useAuthStore();
  // Assuming the token is a JWT that can be directly used
  // In a real application, you might want to verify this token with your backend
  // or fetch user details from your backend using this token.
  // For now, we'll just store it.
  authStore.setToken(token);
  // Optionally, fetch user profile after setting the token
  const userProfile = await fetchUserProfile();
  authStore.setUser(userProfile);
  return { access_token: token, token_type: 'bearer', user: userProfile };
};


export interface UserProfileData {
  username: string;
  email?: string | null;
  phone?: string | null;
  department: string; // Required
  first_name?: string | null; // Optional
  surname?: string | null; // Optional
  is_active: boolean; // Assuming backend int 1/0 maps to boolean
  avatar?: string | null; // Add avatar field
  // Add other fields if needed from the backend User schema
}

export const fetchUserProfile = async (): Promise<UserProfileData> => {
  const headers = getAuthHeaders();
  const response = await fetch(`${API_BASE_URL}/users/me`, {
    method: 'GET',
    headers: {
      ...headers,
      'Content-Type': 'application/json',
    },
  });
  return handleResponse(response);
};

export const updateUserProfile = async (userData: UserProfileData): Promise<UserProfileData> => {
  const headers = getAuthHeaders();
  const response = await fetch(`${API_BASE_URL}/users/me`, {
    method: 'PUT',
    headers: {
      ...headers,
      'Content-Type': 'application/json',
    },
    body: JSON.stringify(userData),
  });
  return handleResponse(response);
};

export const uploadUserAvatar = async (file: File): Promise<{ avatar_url: string }> => {
  const headers = getAuthHeaders();
  const formData = new FormData();
  formData.append('file', file); // 'file' should match the backend expected field name

  const response = await fetch(`${API_BASE_URL}/files/upload_avatar`, {
    method: 'POST',
    headers: {
      ...headers,
      // Do NOT set 'Content-Type' for FormData, the browser sets it automatically with the correct boundary
    },
    body: formData,
  });
  return handleResponse(response);
};


// Helper to get auth headers
export const getAuthHeaders = (): { [key: string]: string } => {
  const authStore = useAuthStore();
  if (authStore.token) {
    return {
      'Authorization': `Bearer ${authStore.token}`,
    };
  }
  return {};
};

export const fetchUiPermissions = async (components: string[]): Promise<Record<string, Record<string, boolean>>> => {
  const headers = getAuthHeaders();
  if (Object.keys(headers).length === 0) {
    // If no auth token, no permissions can be fetched. Return empty object.
    return Promise.resolve({});
  }
  const componentsQuery = components.join(',');
  const response = await fetch(`${API_BASE_URL}/ui_permissions?components=${componentsQuery}`, {
    method: 'GET',
    headers: {
      ...headers,
      'Content-Type': 'application/json',
    },
  });
  return handleResponse(response);
};
// Example of a protected API call
// export const fetchProtectedData = async (): Promise<any> => {
//   const headers = getAuthHeaders();
//   const response = await fetch(`${API_BASE_URL}/protected`, {
//     method: 'GET',
//     headers: {
//       ...headers,
//       'Content-Type': 'application/json',
//     },
//   });
//   return handleResponse(response);
// };
//   const response = await fetch(`${API_BASE_URL}/protected`, {
//     method: 'GET',
//     headers: {
//       ...headers,
//       'Content-Type': 'application/json',
//     },
//   });
//   return handleResponse(response);
// };