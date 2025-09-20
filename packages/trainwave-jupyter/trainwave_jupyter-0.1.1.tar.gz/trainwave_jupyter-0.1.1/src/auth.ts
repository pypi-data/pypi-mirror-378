import { ISettingRegistry } from '@jupyterlab/settingregistry';
import { TrainwaveApiClient, CLIAuthStatus, TrainwaveUser } from './api-client';

export interface AuthToken {
  api_token?: string;
  access_token?: string; // For backward compatibility
  user?: TrainwaveUser;
  expires_at?: number;
}

export interface AuthConfig {
  endpoint: string;
  polling_timeout: number; // in seconds
  polling_interval: number; // in seconds
}

export class AuthService {
  private _settings: ISettingRegistry.ISettings | null = null;
  private _config: AuthConfig;
  private _token: AuthToken | null = null;
  private _apiClient: TrainwaveApiClient;

  constructor(config: AuthConfig, settings?: ISettingRegistry.ISettings) {
    this._config = config;
    this._settings = settings || null;
    this._apiClient = new TrainwaveApiClient(null, config.endpoint);
    this._loadToken();
  }

  /**
   * Check if user is authenticated
   */
  isAuthenticated(): boolean {
    if (!this._token) {
      return false;
    }

    // Check if token is expired
    if (this._token.expires_at && Date.now() >= this._token.expires_at) {
      this._clearToken();
      return false;
    }

    return true;
  }

  /**
   * Get the current API token
   */
  getToken(): string | null {
    if (!this.isAuthenticated()) {
      return null;
    }
    return this._token?.api_token || this._token?.access_token || null;
  }

  /**
   * Get the current configuration
   */
  getConfig(): AuthConfig {
    return this._config;
  }

  /**
   * Get the current user
   */
  getUser(): TrainwaveUser | null {
    if (!this.isAuthenticated()) {
      return null;
    }
    return this._token?.user || null;
  }

  /**
   * Get the API client
   */
  getApiClient(): TrainwaveApiClient {
    // Ensure the API client has the current API key
    const token = this.getToken();
    if (token) {
      this._apiClient.setApiKey(token);
    }
    return this._apiClient;
  }

  /**
   * Get the API key
   */
  getApiKey(): string | null {
    return this.getToken();
  }

  /**
   * Start the authentication flow using CLI-style session-based auth
   */
  async authenticate(): Promise<boolean> {
    try {
      // Create authentication session
      const sessionResponse = await this._apiClient.createCliAuthSession();
      const { url: sessionUrl, token: sessionToken } = sessionResponse;

      console.log('Opening your browser to complete the login.');
      console.log(`URL: ${sessionUrl}`);

      // Open the authentication URL in a new window
      const authWindow = window.open(
        sessionUrl,
        'trainwave-auth',
        'width=600,height=700,scrollbars=yes,resizable=yes'
      );

      if (!authWindow) {
        throw new Error(
          'Failed to open authentication window. Please allow popups.'
        );
      }

      // Poll for authentication completion
      const apiToken = await this._pollForAuthCompletion(sessionToken);

      if (apiToken) {
        // Test the token by getting user info
        this._apiClient.setApiKey(apiToken);
        const user = await this._apiClient.getMyself();

        console.log('✅ Success!');
        console.log(`Logged in as: ${user.email}`);

        // Store the token and user info
        this._token = {
          api_token: apiToken,
          user: user
        };

        // Update the API client with the new API key
        this._apiClient.setApiKey(apiToken);

        await this._saveToken();
        return true;
      } else {
        throw new Error('Authentication failed or timed out');
      }
    } catch (error) {
      console.error('Authentication error:', error);
      throw error;
    }
  }

  /**
   * Logout and clear stored token and all user settings from disk
   */
  async logout(): Promise<void> {
    // Clear token from memory
    this._clearToken();
    // Clear the API key from the API client
    this._apiClient.setApiKey(null);

    // Clear all data from disk
    await Promise.all([
      this._clearTokenFromDisk(),
      this._clearAllSettingsFromDisk()
    ]);
  }

  /**
   * Poll for authentication completion
   */
  private async _pollForAuthCompletion(
    sessionToken: string
  ): Promise<string | null> {
    const endPollingAt = Date.now() + this._config.polling_timeout * 1000;

    while (Date.now() < endPollingAt) {
      try {
        const { status, api_token } =
          await this._apiClient.checkCliAuthSessionStatus(sessionToken);

        if (status === CLIAuthStatus.SUCCESS && api_token) {
          return api_token;
        }

        // Wait before next poll
        await new Promise(resolve =>
          setTimeout(resolve, this._config.polling_interval * 1000)
        );
      } catch (error) {
        console.error('Error checking auth status:', error);
        // Continue polling on error
        await new Promise(resolve =>
          setTimeout(resolve, this._config.polling_interval * 1000)
        );
      }
    }

    return null; // Timeout
  }

  /**
   * Load token from settings
   */
  private _loadToken(): void {
    if (!this._settings) {
      return;
    }

    try {
      const tokenData = this._settings.get('token').composite as any;
      if (tokenData && (tokenData.api_token || tokenData.access_token)) {
        this._token = tokenData;
        // Update the API client with the loaded API key
        const apiKey = tokenData.api_token || tokenData.access_token;
        if (apiKey) {
          this._apiClient.setApiKey(apiKey);
        }
      }
    } catch (error) {
      console.warn('Failed to load token from settings:', error);
    }
  }

  /**
   * Save token to settings
   */
  private async _saveToken(): Promise<void> {
    if (!this._settings) {
      return;
    }

    try {
      await this._settings.set('token', this._token as any);
    } catch (error) {
      console.error('Failed to save token:', error);
    }
  }

  /**
   * Clear the stored token
   */
  private _clearToken(): void {
    this._token = null;
  }

  /**
   * Clear token from disk
   */
  private async _clearTokenFromDisk(): Promise<void> {
    if (!this._settings) {
      return;
    }

    try {
      // Set token to empty but valid structure to clear from disk
      await this._settings.set('token', {
        access_token: '',
        refresh_token: '',
        expires_at: 0,
        token_type: ''
      });
    } catch (error) {
      console.error('Failed to clear token from disk:', error);
    }
  }

  /**
   * Clear all user settings from disk
   */
  private async _clearAllSettingsFromDisk(): Promise<void> {
    if (!this._settings) {
      return;
    }

    try {
      // Set settings to default values to clear from disk (schema requires specific properties)
      await this._settings.set('settings', {
        organization_id: '',
        organization_rid: '',
        project_id: '',
        project_rid: '',
        gpu_type: 'CPU',
        gpu_count: 1
      });
    } catch (error) {
      console.error('Failed to clear settings from disk:', error);
    }
  }

  /**
   * Load settings from the settings registry
   */
  loadSettings(): {
    organization_id: string;
    organization_rid: string;
    project_id: string;
    project_rid: string;
    gpu_type: string;
    gpu_count: number;
  } {
    if (!this._settings) {
      return {
        organization_id: '',
        organization_rid: '',
        project_id: '',
        project_rid: '',
        gpu_type: 'CPU',
        gpu_count: 1
      };
    }

    try {
      const settings = (this._settings.get('settings').composite as any) || {};
      return {
        organization_id: settings.organization_id || '',
        organization_rid: settings.organization_rid || '',
        project_id: settings.project_id || '',
        project_rid: settings.project_rid || '',
        gpu_type: settings.gpu_type || 'CPU',
        gpu_count: settings.gpu_count || 1
      };
    } catch (error) {
      console.warn('Could not load settings:', error);
      return {
        organization_id: '',
        organization_rid: '',
        project_id: '',
        project_rid: '',
        gpu_type: 'CPU',
        gpu_count: 1
      };
    }
  }

  /**
   * Save settings to the settings registry
   */
  async saveSettings(settings: {
    organization_id?: string;
    organization_rid?: string;
    project_id?: string;
    project_rid?: string;
    gpu_type?: string;
    gpu_count?: number;
  }): Promise<void> {
    if (!this._settings) {
      console.warn('No settings registry available');
      return;
    }

    try {
      const currentSettings =
        (this._settings.get('settings').composite as any) || {};
      const updatedSettings = { ...currentSettings, ...settings };
      await this._settings.set('settings', updatedSettings);
    } catch (error) {
      console.error('Failed to save settings:', error);
    }
  }
}
