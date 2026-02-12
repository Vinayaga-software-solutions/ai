<?php

namespace App\Providers;

use Illuminate\Support\Facades\Storage;
use Illuminate\Support\ServiceProvider;
use Google\Cloud\Storage\StorageClient;
use League\Flysystem\Filesystem;
use League\Flysystem\GoogleCloudStorage\GoogleCloudStorageAdapter;
use League\Flysystem\GoogleCloudStorage\UniformBucketLevelAccessVisibility;
use Illuminate\Filesystem\FilesystemAdapter;

class GcsServiceProvider extends ServiceProvider
{
    public function boot()
    {
        Storage::extend('gcs', function ($app, $config) {
            $clientConfig = [
                'projectId' => $config['project_id'] ?? null,
            ];
            if (!empty($config['key_file_path'])) {
                $clientConfig['keyFilePath'] = $config['key_file_path'];
            }

            $client = new StorageClient($clientConfig);

            $bucket = $client->bucket($config['bucket']);

            $adapter = new GoogleCloudStorageAdapter(
                $bucket,
                $config['path_prefix'] ?? '',
                new UniformBucketLevelAccessVisibility(),
            );

            return new FilesystemAdapter(
                new Filesystem($adapter),
                $adapter,
                $config
            );
        });
    }
}
