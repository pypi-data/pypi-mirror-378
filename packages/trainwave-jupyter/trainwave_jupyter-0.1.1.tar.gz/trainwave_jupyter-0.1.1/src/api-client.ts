import { requestAPI } from './handler';

export interface TrainwaveUser {
  id: string;
  rid: string;
  email: string;
  first_name?: string;
  last_name?: string;
  picture?: string;
}

export interface TrainwaveOrganization {
  id: string;
  rid: string;
  name: string;
  computed_credit_balance: number;
}

export interface TrainwaveProject {
  id: string;
  rid: string;
  name: string;
  active_job_count: number;
  total_job_count: number;
  created_at: string;
  updated_at: string;
  organization: string;
  users: string[];
}

export enum JobStatus {
  SUBMIT_CODE = 'SUBMIT_CODE',
  LAUNCHING = 'LAUNCHING',
  RUNNING = 'RUNNING',
  ERROR = 'ERROR',
  UPLOADING = 'UPLOADING',
  SUCCESS = 'SUCCESS',
  USER_PROCESS_FAILED = 'USER_PROCESS_FAILED',
  SYSTEM_TERMINATED = 'SYSTEM_TERMINATED',
  USER_CANCELLED = 'USER_CANCELLED'
}

export interface CloudOffer {
  cpus: number;
  memory_mb: number;
  compliance_soc2: boolean;
  gpu_type?: string;
  gpu_memory_mb: number;
  gpus: number;
}

export interface JobConfig {
  id: string;
  rid: string;
  name: string;
  expires_at: number;
  cpus: number;
  gpus: number;
  gpu_type?: string;
}

export interface Job {
  id: string;
  rid: string;
  state: JobStatus;
  s3_url: string;
  project: TrainwaveProject;
  cloud_offer: CloudOffer;
  cost_per_hour: number;
  config: JobConfig;
  created_at: string; // ISO datetime string
  total_cost: number;
  upload_url: string;
  url?: string;
}

export enum CLIAuthStatus {
  NOT_FOUND = 'NOT_FOUND',
  NOT_COMPLETED = 'NOT_COMPLETED',
  SUCCESS = 'SUCCESS'
}

export interface AuthSessionResponse {
  url: string;
  token: string;
}

export interface SessionStatusResponse {
  status: CLIAuthStatus;
  api_token?: string;
}

export class TrainwaveApiClient {
  private apiKey: string | null = null;
  private endpoint: string;
  private project: string = '';
  private organization: string = '';

  constructor(
    apiKey: string | null = null,
    endpoint: string = 'https://backend.trainwave.ai'
  ) {
    this.apiKey = apiKey;
    this.endpoint = endpoint.replace(/\/$/, ''); // Remove trailing slash
  }

  /**
   * Get the endpoint URL
   */
  getEndpoint(): string {
    return this.endpoint;
  }

  /**
   * Get the current project
   */
  getProject(): string {
    return this.project;
  }

  /**
   * Get the current organization
   */
  getOrganization(): string {
    return this.organization;
  }

  /**
   * Create a CLI authentication session
   */
  async createCliAuthSession(): Promise<AuthSessionResponse> {
    const response = await requestAPI<AuthSessionResponse>(
      'auth/create_session',
      {
        method: 'POST',
        body: JSON.stringify({
          name: navigator.userAgent // Use user agent as device name
        })
      }
    );
    return response;
  }

  /**
   * Check CLI authentication session status
   */
  async checkCliAuthSessionStatus(
    token: string
  ): Promise<SessionStatusResponse> {
    const response = await requestAPI<SessionStatusResponse>(
      'auth/session_status',
      {
        method: 'POST',
        body: JSON.stringify({ token })
      }
    );
    return response;
  }

  /**
   * Get current user information
   */
  async getMyself(): Promise<TrainwaveUser> {
    if (!this.apiKey) {
      throw new Error('API key is required');
    }

    const response = await requestAPI<TrainwaveUser>('api/users/me', {
      method: 'GET',
      headers: {
        'X-Api-Key': this.apiKey
      }
    });
    return response;
  }

  /**
   * List organizations
   */
  async listOrganizations(): Promise<TrainwaveOrganization[]> {
    if (!this.apiKey) {
      throw new Error('API key is required');
    }

    const response = await requestAPI<{ results: TrainwaveOrganization[] }>(
      'api/organizations',
      {
        method: 'GET',
        headers: {
          'X-Api-Key': this.apiKey
        }
      }
    );
    return response.results;
  }

  /**
   * List projects
   */
  async listProjects(organizationId?: string): Promise<TrainwaveProject[]> {
    if (!this.apiKey) {
      throw new Error('API key is required');
    }

    const path = organizationId
      ? `api/projects?org=${organizationId}`
      : 'api/projects';

    const response = await requestAPI<{ results: TrainwaveProject[] }>(path, {
      method: 'GET',
      headers: {
        'X-Api-Key': this.apiKey
      }
    });
    return response.results;
  }

  /**
   * Create a new project
   */
  async createProject(
    name: string,
    organizationId: string
  ): Promise<TrainwaveProject> {
    if (!this.apiKey) {
      throw new Error('API key is required');
    }

    const response = await requestAPI<TrainwaveProject>('api/projects', {
      method: 'POST',
      headers: {
        'X-Api-Key': this.apiKey,
        'Content-Type': 'application/json'
      },
      body: JSON.stringify({
        name: name,
        organization: organizationId
      })
    });
    return response;
  }

  /**
   * List jobs
   */
  async listJobs(organizationId?: string, projectId?: string): Promise<Job[]> {
    if (!this.apiKey) {
      throw new Error('API key is required');
    }

    let path = 'api/jobs';
    const params = new URLSearchParams();

    if (organizationId) {
      params.append('org', organizationId);
    }

    if (projectId) {
      params.append('project', projectId);
    }

    if (params.toString()) {
      path += `?${params.toString()}`;
    }

    const response = await requestAPI<{ results: Job[] }>(path, {
      method: 'GET',
      headers: {
        'X-Api-Key': this.apiKey
      }
    });
    return response.results;
  }

  /**
   * Check if API key is valid
   */
  async checkApiKey(): Promise<boolean> {
    if (!this.apiKey) {
      return false;
    }

    try {
      const response = await requestAPI<{ results: any[] }>(
        'api/organizations',
        {
          method: 'GET',
          headers: {
            'X-Api-Key': this.apiKey
          }
        }
      );
      return response.results.length > 0;
    } catch (error) {
      return false;
    }
  }

  /**
   * Set API key
   */
  setApiKey(apiKey: string | null): void {
    this.apiKey = apiKey;
  }

  /**
   * Get API key
   */
  getApiKey(): string | null {
    return this.apiKey;
  }

  /**
   * Set project
   */
  setProject(project: string): void {
    this.project = project;
  }

  /**
   * Set organization
   */
  setOrganization(organization: string): void {
    this.organization = organization;
  }

  /**
   * List available GPU offers
   */
  async listOffers(): Promise<any[]> {
    if (!this.apiKey) {
      throw new Error('API key is required');
    }

    const response = await requestAPI<{ results: any[] }>('api/offers', {
      method: 'GET',
      headers: {
        'X-Api-Key': this.apiKey
      }
    });
    return response.results;
  }
}
