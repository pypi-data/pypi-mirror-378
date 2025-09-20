/**
 * Comprehensive test suite for the Trainwave JupyterLab extension
 */

import { ServerConnection } from '@jupyterlab/services';
import { ISettingRegistry } from '@jupyterlab/settingregistry';

import * as handler from '../handler';
import { AuthService, AuthConfig } from '../auth';
import {
  TrainwaveApiClient,
  CLIAuthStatus,
  TrainwaveUser,
  TrainwaveOrganization,
  TrainwaveProject,
  Job,
  JobStatus
} from '../api-client';

// Mock the JupyterLab modules
jest.mock('@jupyterlab/application');
jest.mock('@jupyterlab/notebook');
jest.mock('@jupyterlab/settingregistry');
jest.mock('@jupyterlab/services');

describe('Trainwave Extension', () => {
  beforeEach(() => {
    // Reset all mocks
    jest.clearAllMocks();
  });

  describe('Basic functionality', () => {
    it('should be tested', () => {
      expect(1 + 1).toEqual(2);
    });
  });
});

describe('requestAPI', () => {
  beforeEach(() => {
    jest.clearAllMocks();
  });

  it('should make API requests correctly', async () => {
    const mockResponse = { data: 'test response' };
    const mockFetch = jest.fn().mockResolvedValue({
      ok: true,
      text: jest.fn().mockResolvedValue(JSON.stringify(mockResponse))
    });

    // Mock ServerConnection
    (ServerConnection.makeSettings as jest.Mock).mockReturnValue({
      baseUrl: 'http://localhost:8888'
    });
    (ServerConnection.makeRequest as jest.Mock).mockImplementation(mockFetch);

    const result = await handler.requestAPI('test-endpoint');

    expect(result).toEqual(mockResponse);
    expect(mockFetch).toHaveBeenCalledWith(
      'http://localhost:8888/trainwave-jupyter/test-endpoint',
      {},
      expect.any(Object)
    );
  });

  it('should handle non-JSON responses', async () => {
    const mockFetch = jest.fn().mockResolvedValue({
      ok: true,
      text: jest.fn().mockResolvedValue('plain text response')
    });

    (ServerConnection.makeSettings as jest.Mock).mockReturnValue({
      baseUrl: 'http://localhost:8888'
    });
    (ServerConnection.makeRequest as jest.Mock).mockImplementation(mockFetch);

    const result = await handler.requestAPI('test-endpoint');

    expect(result).toBe('plain text response');
  });
});

describe('AuthService', () => {
  let authService: AuthService;
  let mockConfig: AuthConfig;
  let mockSettings: jest.Mocked<ISettingRegistry.ISettings>;

  beforeEach(() => {
    mockConfig = {
      endpoint: 'https://test.trainwave.ai',
      polling_timeout: 300,
      polling_interval: 2
    };

    mockSettings = {
      get: jest.fn(),
      set: jest.fn()
    } as any;

    authService = new AuthService(mockConfig, mockSettings);
  });

  describe('Initialization', () => {
    it('should initialize with correct config', () => {
      expect(authService.getConfig()).toEqual(mockConfig);
    });

    it('should initialize without settings', () => {
      const service = new AuthService(mockConfig);
      expect(service.getConfig()).toEqual(mockConfig);
    });
  });

  describe('Authentication state', () => {
    it('should not be authenticated initially', () => {
      expect(authService.isAuthenticated()).toBe(false);
    });

    it('should return null token when not authenticated', () => {
      expect(authService.getToken()).toBe(null);
    });

    it('should return null user when not authenticated', () => {
      expect(authService.getUser()).toBe(null);
    });
  });

  describe('Token management', () => {
    it('should load token from settings', () => {
      const mockToken = {
        api_token: 'test-token',
        user: { id: '1', email: 'test@example.com' } as TrainwaveUser
      };

      mockSettings.get.mockReturnValue({
        composite: mockToken
      } as any);

      const service = new AuthService(mockConfig, mockSettings);
      expect(service.isAuthenticated()).toBe(true);
      expect(service.getToken()).toBe('test-token');
    });

    it('should handle expired token', () => {
      const expiredToken = {
        api_token: 'test-token',
        expires_at: Date.now() - 1000 // Expired 1 second ago
      };

      mockSettings.get.mockReturnValue({
        composite: expiredToken
      } as any);

      const service = new AuthService(mockConfig, mockSettings);
      expect(service.isAuthenticated()).toBe(false);
    });

    it('should save token to settings', async () => {
      const mockToken = {
        api_token: 'test-token',
        user: { id: '1', email: 'test@example.com' } as TrainwaveUser
      };

      // Mock the internal token setting
      (authService as any)._token = mockToken;

      await (authService as any)._saveToken();

      expect(mockSettings.set).toHaveBeenCalledWith('token', mockToken);
    });
  });

  describe('Settings management', () => {
    it('should load settings with defaults', () => {
      mockSettings.get.mockReturnValue({
        composite: {}
      } as any);

      const settings = authService.loadSettings();
      expect(settings).toEqual({
        organization_id: '',
        organization_rid: '',
        project_id: '',
        project_rid: '',
        gpu_type: 'CPU',
        gpu_count: 1
      });
    });

    it('should load custom settings', () => {
      const customSettings = {
        organization_id: 'org-123',
        organization_rid: 'org-rid-123',
        project_id: 'proj-123',
        project_rid: 'proj-rid-123',
        gpu_type: 'V100',
        gpu_count: 2
      };

      mockSettings.get.mockReturnValue({
        composite: customSettings
      } as any);

      const settings = authService.loadSettings();
      expect(settings).toEqual(customSettings);
    });

    it('should save settings', async () => {
      const newSettings = {
        project_id: 'proj-456',
        gpu_type: 'A100',
        gpu_count: 4
      };

      mockSettings.get.mockReturnValue({
        composite: { project_id: 'old-proj' }
      } as any);

      await authService.saveSettings(newSettings);

      expect(mockSettings.set).toHaveBeenCalledWith('settings', {
        ...newSettings
      });
    });
  });

  describe('Logout', () => {
    it('should clear token and settings from disk on logout', async () => {
      // Set up authenticated state
      (authService as any)._token = {
        api_token: 'test-token',
        user: { id: '1', email: 'test@example.com' } as TrainwaveUser
      };

      // Set up some settings
      await authService.saveSettings({
        project_id: 'test-project',
        gpu_type: 'V100',
        gpu_count: 2
      });

      // Clear previous calls
      mockSettings.set.mockClear();

      await authService.logout();

      expect(authService.isAuthenticated()).toBe(false);
      expect(authService.getToken()).toBe(null);

      // Verify both token and settings are cleared from disk
      expect(mockSettings.set).toHaveBeenCalledWith('token', {
        access_token: '',
        refresh_token: '',
        expires_at: 0,
        token_type: ''
      });
      expect(mockSettings.set).toHaveBeenCalledWith('settings', {
        organization_id: '',
        organization_rid: '',
        project_id: '',
        project_rid: '',
        gpu_type: 'CPU',
        gpu_count: 1
      });
      expect(mockSettings.set).toHaveBeenCalledTimes(2);
    });

    it('should handle logout when settings registry is not available', async () => {
      // Create auth service without settings registry
      const authServiceWithoutSettings = new AuthService({
        endpoint: 'https://test.com',
        polling_timeout: 300,
        polling_interval: 2
      });

      // Set up authenticated state
      (authServiceWithoutSettings as any)._token = {
        api_token: 'test-token',
        user: { id: '1', email: 'test@example.com' } as TrainwaveUser
      };

      // Should not throw error even without settings registry
      await expect(authServiceWithoutSettings.logout()).resolves.not.toThrow();

      expect(authServiceWithoutSettings.isAuthenticated()).toBe(false);
      expect(authServiceWithoutSettings.getToken()).toBe(null);
    });
  });
});

describe('TrainwaveApiClient', () => {
  let apiClient: TrainwaveApiClient;

  beforeEach(() => {
    apiClient = new TrainwaveApiClient(
      'test-api-key',
      'https://test.trainwave.ai'
    );
  });

  describe('Initialization', () => {
    it('should initialize with API key and endpoint', () => {
      expect(apiClient.getApiKey()).toBe('test-api-key');
      expect(apiClient.getEndpoint()).toBe('https://test.trainwave.ai');
    });

    it('should remove trailing slash from endpoint', () => {
      const client = new TrainwaveApiClient(null, 'https://test.trainwave.ai/');
      expect(client.getEndpoint()).toBe('https://test.trainwave.ai');
    });
  });

  describe('API Key management', () => {
    it('should set and get API key', () => {
      apiClient.setApiKey('new-api-key');
      expect(apiClient.getApiKey()).toBe('new-api-key');
    });

    it('should clear API key', () => {
      apiClient.setApiKey(null);
      expect(apiClient.getApiKey()).toBe(null);
    });
  });

  describe('Project and Organization management', () => {
    it('should set and get project', () => {
      apiClient.setProject('test-project');
      expect(apiClient.getProject()).toBe('test-project');
    });

    it('should set and get organization', () => {
      apiClient.setOrganization('test-org');
      expect(apiClient.getOrganization()).toBe('test-org');
    });
  });

  describe('Authentication methods', () => {
    beforeEach(() => {
      // Mock requestAPI
      jest.spyOn(handler, 'requestAPI').mockImplementation(jest.fn());
    });

    it('should create CLI auth session', async () => {
      const mockResponse = {
        url: 'https://app.trainwave.ai/auth/test',
        token: 'session-token'
      };

      (handler.requestAPI as jest.Mock).mockResolvedValue(mockResponse);

      const result = await apiClient.createCliAuthSession();

      expect(result).toEqual(mockResponse);
      expect(handler.requestAPI).toHaveBeenCalledWith('auth/create_session', {
        method: 'POST',
        body: JSON.stringify({
          name: navigator.userAgent
        })
      });
    });

    it('should check CLI auth session status', async () => {
      const mockResponse = {
        status: CLIAuthStatus.SUCCESS,
        api_token: 'api-token'
      };

      (handler.requestAPI as jest.Mock).mockResolvedValue(mockResponse);

      const result = await apiClient.checkCliAuthSessionStatus('session-token');

      expect(result).toEqual(mockResponse);
      expect(handler.requestAPI).toHaveBeenCalledWith('auth/session_status', {
        method: 'POST',
        body: JSON.stringify({ token: 'session-token' })
      });
    });
  });

  describe('API methods requiring authentication', () => {
    beforeEach(() => {
      jest.spyOn(handler, 'requestAPI').mockImplementation(jest.fn());
    });

    it('should throw error when API key is missing', async () => {
      const client = new TrainwaveApiClient(null);

      await expect(client.getMyself()).rejects.toThrow('API key is required');
      await expect(client.listOrganizations()).rejects.toThrow(
        'API key is required'
      );
      await expect(client.listProjects()).rejects.toThrow(
        'API key is required'
      );
      await expect(client.listJobs()).rejects.toThrow('API key is required');
      await expect(client.listOffers()).rejects.toThrow('API key is required');
    });

    it('should get user information', async () => {
      const mockUser: TrainwaveUser = {
        id: '1',
        rid: 'rid-1',
        email: 'test@example.com',
        first_name: 'Test',
        last_name: 'User'
      };

      (handler.requestAPI as jest.Mock).mockResolvedValue(mockUser);

      const result = await apiClient.getMyself();

      expect(result).toEqual(mockUser);
      expect(handler.requestAPI).toHaveBeenCalledWith('api/users/me', {
        method: 'GET',
        headers: {
          'X-Api-Key': 'test-api-key'
        }
      });
    });

    it('should list organizations', async () => {
      const mockOrgs: TrainwaveOrganization[] = [
        {
          id: '1',
          rid: 'rid-1',
          name: 'Test Org',
          computed_credit_balance: 100.0
        }
      ];

      (handler.requestAPI as jest.Mock).mockResolvedValue({
        results: mockOrgs
      });

      const result = await apiClient.listOrganizations();

      expect(result).toEqual(mockOrgs);
      expect(handler.requestAPI).toHaveBeenCalledWith('api/organizations', {
        method: 'GET',
        headers: {
          'X-Api-Key': 'test-api-key'
        }
      });
    });

    it('should list projects', async () => {
      const mockProjects: TrainwaveProject[] = [
        {
          id: '1',
          rid: 'rid-1',
          name: 'Test Project',
          active_job_count: 2,
          total_job_count: 5,
          created_at: '2023-01-01T00:00:00Z',
          updated_at: '2023-01-02T00:00:00Z',
          organization: 'org-1',
          users: ['user-1']
        }
      ];

      (handler.requestAPI as jest.Mock).mockResolvedValue({
        results: mockProjects
      });

      const result = await apiClient.listProjects();

      expect(result).toEqual(mockProjects);
      expect(handler.requestAPI).toHaveBeenCalledWith('api/projects', {
        method: 'GET',
        headers: {
          'X-Api-Key': 'test-api-key'
        }
      });
    });

    it('should list jobs', async () => {
      const mockJobs: Job[] = [
        {
          id: '1',
          rid: 'rid-1',
          state: JobStatus.RUNNING,
          s3_url: 's3://bucket/key',
          project: {} as TrainwaveProject,
          cloud_offer: {
            cpus: 4,
            memory_mb: 8192,
            compliance_soc2: true,
            gpu_type: 'A100',
            gpu_memory_mb: 40960,
            gpus: 1
          },
          cost_per_hour: 2.5,
          config: {
            id: '1',
            rid: 'rid-1',
            name: 'test-config',
            expires_at: Date.now() + 3600000,
            cpus: 4,
            gpus: 1,
            gpu_type: 'A100'
          },
          created_at: '2023-01-01T00:00:00Z',
          total_cost: 5.0,
          upload_url: 'https://upload.url'
        }
      ];

      (handler.requestAPI as jest.Mock).mockResolvedValue({
        results: mockJobs
      });

      const result = await apiClient.listJobs();

      expect(result).toEqual(mockJobs);
      expect(handler.requestAPI).toHaveBeenCalledWith('api/jobs', {
        method: 'GET',
        headers: {
          'X-Api-Key': 'test-api-key'
        }
      });
    });

    it('should list jobs with organization filter', async () => {
      const mockJobs: Job[] = [];

      (handler.requestAPI as jest.Mock).mockResolvedValue({
        results: mockJobs
      });

      await apiClient.listJobs('org-123');

      expect(handler.requestAPI).toHaveBeenCalledWith('api/jobs?org=org-123', {
        method: 'GET',
        headers: {
          'X-Api-Key': 'test-api-key'
        }
      });
    });

    it('should list jobs with organization and project filters', async () => {
      const mockJobs: Job[] = [];

      (handler.requestAPI as jest.Mock).mockResolvedValue({
        results: mockJobs
      });

      await apiClient.listJobs('org-123', 'proj-456');

      expect(handler.requestAPI).toHaveBeenCalledWith(
        'api/jobs?org=org-123&project=proj-456',
        {
          method: 'GET',
          headers: {
            'X-Api-Key': 'test-api-key'
          }
        }
      );
    });

    it('should list offers', async () => {
      const mockOffers = [
        {
          id: '1',
          cpus: 4,
          memory_mb: 8192,
          gpus: 1,
          gpu_type: 'A100',
          gpu_memory_mb: 40960,
          compliance_soc2: true
        }
      ];

      (handler.requestAPI as jest.Mock).mockResolvedValue({
        results: mockOffers
      });

      const result = await apiClient.listOffers();

      expect(result).toEqual(mockOffers);
      expect(handler.requestAPI).toHaveBeenCalledWith('api/offers', {
        method: 'GET',
        headers: {
          'X-Api-Key': 'test-api-key'
        }
      });
    });

    it('should check API key validity', async () => {
      (handler.requestAPI as jest.Mock).mockResolvedValue({
        results: [{ id: '1' }]
      });

      const result = await apiClient.checkApiKey();

      expect(result).toBe(true);
    });

    it('should return false for invalid API key', async () => {
      (handler.requestAPI as jest.Mock).mockRejectedValue(
        new Error('Unauthorized')
      );

      const result = await apiClient.checkApiKey();

      expect(result).toBe(false);
    });

    it('should return false when no API key is set', async () => {
      const client = new TrainwaveApiClient(null);
      const result = await client.checkApiKey();
      expect(result).toBe(false);
    });
  });
});
