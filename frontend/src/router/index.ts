import { createRouter, createWebHistory } from 'vue-router';
import type { RouteLocationNormalized, NavigationGuardNext, RouteLocationNormalizedLoaded } from 'vue-router/dist/vue-router.d.ts';
import { useAuthStore } from '../stores/auth'; // Import the auth store
import i18n from '../locales'; // Import the i18n instance
import { Role } from '@/services/apiService'; // Import Role interface
import NotFound from '../views/ErrorPages/NotFound.vue'; // Import NotFound component
import PermissionDenied from '../views/ErrorPages/PermissionDenied.vue'; // Import PermissionDenied component (corrected filename)
import GeneralError from '../views/ErrorPages/GeneralError.vue'; // Import GeneralError component
import { handleThirdPartyAuthCallback } from '../services/authService'; // Import the new auth service function

const router = createRouter({
  history: createWebHistory(),
  routes: [
    {
      path: '/login',
      name: 'Login',
      component: () => import('../views/Login.vue'),
    },
    {
      path: '/register',
      name: 'Register',
      component: () => import('../views/Register.vue'),
    },
    {
      path: '/forgot-password',
      name: 'ForgotPassword',
      component: () => import('../views/ForgotPassword.vue'),
    },
    {
      path: '/reset-password',
      name: 'ResetPassword',
      component: () => import('../views/ResetPassword.vue'),
    },
    {
      path: '/activate',
      name: 'ActivateAccount',
      component: () => import('../views/ActivateAccount.vue'),
    },
    {
      path: '/auth/callback', // New route for OAuth callbacks
      name: 'OAuthCallback',
      component: {
        template: '<div>Loading...</div>', // Simple placeholder component
        async beforeRouteEnter(to: RouteLocationNormalized, from: RouteLocationNormalized, next: NavigationGuardNext) {
          console.log('OAuthCallback route entered. Query params:', to.query);
          const token = to.query.token as string;
          if (token) {
            console.log('Token found in query params:', token);
            try {
              const authStore = useAuthStore();
              await handleThirdPartyAuthCallback(token);
              console.log('handleThirdPartyAuthCallback completed. Redirecting to /rag-intro');
              next('/rag-intro');
            } catch (error) {
              console.error('OAuth callback error:', error);
              // Redirect to login or an error page
              next({ name: 'Login', query: { error: 'oauth_failed' } });
            }
          } else {
            // No token found, redirect to login or error
            next({ name: 'Login', query: { error: 'no_oauth_token' } });
          }
        },
      },
    },
    {
      path: '/upload',
      name: 'UploadFile',
      component: () => import('../views/UploadFile.vue'),
      meta: { requiresAuth: true } // Add meta field to indicate protected route
    },
    {
      path: '/query',
      name: 'QueryRAG',
      //component: () => import('../views/QueryRAG.vue'),
      component: () => import('../views/RostiChatInterface.vue'),
      meta: { requiresAuth: true } // Add meta field to indicate protected route
    },
    {
      path: '/chatpage',
      name: 'ChatPage',
      component: () => import('../views/ChatPage.vue'),
      meta: { requiresAuth: true } // Add meta field to indicate protected route
    },
    {
      path: '/rag-intro',
      name: 'RAGIntro',
      component: () => import('../views/RAGIntro.vue'),
      meta: { requiresAuth: true } // Add meta field to indicate protected route
    },
    {
      path: '/profile',
      name: 'UserProfile',
      component: () => import('../views/UserProfile.vue'),
      meta: { requiresAuth: true } // Assuming user profile page requires authentication
    },
    {
      path: '/rag',
      name: 'RagList',
      component: () => import('../views/RagList.vue'),
      props: { i18n: i18n }, // Pass i18n instance as prop
      meta: { requiresAuth: true } // RAG list page requires authentication
    },
    {
      path: '/rag/:id',
      name: 'RagEdit',
      component: () => import('../views/RagEdit.vue'),
      props: (route: RouteLocationNormalizedLoaded) => ({ id: route.params.id, i18n: i18n }), // Pass id and i18n instance as props
      meta: { requiresAuth: true } // RAG edit page requires authentication
    },
    // User Management Routes
    {
      path: '/user-management',
      name: 'UserManagement',
      component: () => import('../views/UserManagement/UserManagement.vue'),
      meta: { requiresAuth: true, roles: ['admin'] } // Requires auth and specific role
    },
    // Role Management Routes
    {
      path: '/role-management',
      name: 'RoleManagement',
      component: () => import('../views/RoleManagement/RoleManagement.vue'),
      meta: { requiresAuth: true, roles: ['admin'] } // Requires auth and specific role
    },
    // Policy Management Route
    {
      path: '/policy-management',
      name: 'PolicyManagement',
      component: () => import('../views/PolicyManagement.vue'),
      meta: { requiresAuth: true, roles: ['admin'] } // Requires auth and specific role
    },
    // Define other protected routes here
    // System Settings Route
    {
      path: '/system-settings',
      name: 'SystemSettings',
      component: () => import('../views/SystemSettings.vue'),
      meta: { requiresAuth: true, roles: ['admin'] } // Requires auth and specific role
    },
    // Error Pages
    {
      path: '/404',
      name: 'NotFound',
      component: NotFound,
    },
    {
      path: '/permission-denied',
      name: 'PermissionDenied',
      component: PermissionDenied,
    },
    {
      path: '/error',
      name: 'GeneralError',
      component: GeneralError,
      props: (route: RouteLocationNormalizedLoaded) => ({ errorMessage: route.query.message }), // Pass error message as prop
    },
    // Add a catch-all redirect for the root path to /upload if authenticated, or /login if not
    {
      path: '/',
      redirect: '/query' // Default redirect for authenticated users
    },
    {
      path: '/:catchAll(.*)', // Catch-all route for 404 or other unmatched paths
      redirect: '/404' // Redirect to 404 page
    }
  ],
});

console.log('Router routes:', router.options.routes); // Add this line for debugging

// Navigation guard
router.beforeEach((to: RouteLocationNormalized, from: RouteLocationNormalized, next: NavigationGuardNext) => {
  const authStore = useAuthStore();
  const localStorageToken = localStorage.getItem('token'); // Check localStorage directly

  // If token exists in localStorage but not in store, update store
  if (localStorageToken && !authStore.token) {
    authStore.setToken(localStorageToken);
    // Note: User info might need to be fetched separately if not stored in localStorage
  }

  // Use the state from the store (which is now potentially updated from localStorage)
  const isAuthenticated = authStore.isAuthenticated;

  // Define routes that do NOT require authentication, including error pages
  const publicRoutes = ['/login', '/register', '/forgot-password', '/reset-password', '/activate', '/404', '/permission-denied', '/error', '/auth/callback'];

  if (isAuthenticated) {
    // If authenticated, redirect away from login/register pages
    if (publicRoutes.includes(to.path) && to.path !== '/404' && to.path !== '/permission-denied' && to.path !== '/error') {
      next('/rag-intro'); // Redirect to a default protected page
    } else {
      // Check for required permission if specified in meta
      // Check for required roles if specified in meta
      if (to.meta.roles && Array.isArray(to.meta.roles)) {
        const userRoles = authStore.user?.roles?.map((r: any) => r.name) || [];
        const hasRole = to.meta.roles.some(role => userRoles.includes(role));

        if (hasRole) {
          next(); // Allow access if user has one of the required roles
        } else {
          // Redirect to the permission denied page
          next('/permission-denied');
        }
      } else {
        next(); // Allow access to protected routes without specific role requirements
      }
    }
  } else {
    // If not authenticated, only allow access to public routes
    if (publicRoutes.includes(to.path)) {
      next(); // Allow access to public routes
    } else {
      next('/login'); // Redirect to login for any other route
    }
  }
});

export default router;