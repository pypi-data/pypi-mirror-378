const jestJupyterLab = require('@jupyterlab/testutils/lib/jest-config');

const esModules = [
    '@codemirror',
    '@jupyter/ydoc',
    '@jupyterlab/',
    'lib0',
    'nanoid',
    'vscode-ws-jsonrpc',
    'y-protocols',
    'y-websocket',
    'yjs'
].join('|');

const baseConfig = jestJupyterLab(__dirname);

module.exports = {
    ...baseConfig,
    automock: false,
    collectCoverageFrom: [
        'src/**/*.{ts,tsx}',
        '!src/**/*.d.ts',
        '!src/**/.ipynb_checkpoints/*',
        '!src/**/__tests__/**',
        '!src/**/*.spec.{ts,tsx}'
    ],
    coverageReporters: ['lcov', 'text', 'html'],
    coverageDirectory: 'coverage',
    testRegex: 'src/.*/.*.spec.ts[x]?$',
    transformIgnorePatterns: [`/node_modules/(?!${esModules}).+`],
    setupFilesAfterEnv: ['<rootDir>/src/__tests__/setup.ts'],
    testEnvironment: 'jsdom',
    globals: {
        'ts-jest': {
            tsconfig: {
                types: ['node', 'jest']
            }
        }
    },
    moduleNameMapper: {
        '\\.(css|less|scss|sass)$': 'identity-obj-proxy',
        '\\.(jpg|jpeg|png|gif|eot|otf|webp|svg|ttf|woff|woff2|mp4|webm|wav|mp3|m4a|aac|oga)$': 'jest-transform-stub'
    },
    collectCoverage: true,
    coverageThreshold: {
        global: {
            branches: 50,
            functions: 50,
            lines: 50,
            statements: 50
        }
    }
};