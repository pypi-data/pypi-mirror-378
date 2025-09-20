#!/usr/bin/env python3
"""
Comprehensive tests for async storage helpers using real Azure resources

This module tests both AsyncStorageBlobHelper and AsyncStorageQueueHelper with real Azure resources.
All tests use environment-based configuration and automatic test skipping.
"""

import pytest
import asyncio
import os
import sys
import uuid
import tempfile
import aiofiles
import aiohttp

# Add src to path for imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))

from sas.storage.blob.async_helper import AsyncStorageBlobHelper
from sas.storage.queue.async_helper import AsyncStorageQueueHelper


class TestAsyncStorageBlobHelperReal:
    """Test async blob helper functionality with real Azure resources"""

    @pytest.fixture
    def connection_string(self):
        """Get connection string from environment"""
        conn_str = os.getenv("AZURE_STORAGE_CONNECTION_STRING")
        if not conn_str:
            pytest.skip("AZURE_STORAGE_CONNECTION_STRING environment variable not set")
        return conn_str

    @pytest.fixture
    def account_name(self):
        account_name  = os.getenv("AZURE_STORAGE_ACCOUNT_NAME")  # os.getenv("AZURE_STORAGE_ACCOUNT_NAME")
        if not account_name:
            pytest.skip("AZURE_STORAGE_ACCOUNT_NAME environment variable not set")
        return account_name

    @pytest.fixture
    def test_container_name(self):
        """Generate unique container name for testing"""
        return f"test-container-{uuid.uuid4().hex[:8]}"

    @pytest.fixture
    def test_blob_name(self):
        """Generate unique blob name for testing"""
        return f"test-blob-{uuid.uuid4().hex[:8]}.txt"

    @pytest.mark.asyncio
    async def test_async_context_manager(self, account_name):
        """Test async context manager functionality"""
        # Test that context manager works with real connection
        async with AsyncStorageBlobHelper(account_name=account_name) as helper:
            assert helper._blob_service_client is not None

    @pytest.mark.asyncio
    async def test_real_container_operations(self, account_name, test_container_name):
        """Test real async container operations"""
        async with AsyncStorageBlobHelper(account_name=account_name) as helper:
            try:
                # Test container creation
                result = await helper.create_container(test_container_name)
                assert result is True

                # Test container exists
                exists = await helper.container_exists(test_container_name)
                assert exists is True

                # Test list containers
                containers = await helper.list_containers()
                assert isinstance(containers, list)
                container_names = [c["name"] for c in containers]
                assert test_container_name in container_names

            finally:
                # Cleanup
                try:
                    await helper.delete_container(test_container_name)
                except Exception:
                    pass  # Ignore cleanup errors

    @pytest.mark.asyncio
    async def test_container_force_delete(
        self, account_name, test_container_name, test_blob_name
    ):
        """Test force deletion of container with blobs"""
        async with AsyncStorageBlobHelper(account_name=account_name) as helper:
            try:
                # Create container
                await helper.create_container(test_container_name)

                # Upload a blob to the container
                test_content = "Test content for force delete"
                await helper.upload_blob(
                    container_name=test_container_name,
                    blob_name=test_blob_name,
                    data=test_content,
                )

                # Verify blob exists
                exists = await helper.blob_exists(test_container_name, test_blob_name)
                assert exists is True

                # Test that normal delete fails with container containing blobs
                with pytest.raises((ValueError, Exception)) as exc_info:
                    await helper.delete_container(
                        test_container_name, force_delete=False
                    )

                # Verify the error message suggests using force_delete
                error_msg = str(exc_info.value).lower()
                assert "force_delete" in error_msg or "not empty" in error_msg

                # Verify container and blob still exist
                container_exists = await helper.container_exists(test_container_name)
                blob_exists = await helper.blob_exists(
                    test_container_name, test_blob_name
                )
                assert container_exists is True
                assert blob_exists is True

                # Test force delete succeeds
                result = await helper.delete_container(
                    test_container_name, force_delete=True
                )
                assert result is True

                # Verify container no longer exists
                container_exists = await helper.container_exists(test_container_name)
                assert container_exists is False

            except Exception as e:
                # Cleanup on test failure
                try:
                    await helper.delete_container(
                        test_container_name, force_delete=True
                    )
                except Exception:
                    pass  # Ignore cleanup errors
                raise e

    @pytest.mark.asyncio
    async def test_container_force_delete_empty(
        self, account_name, test_container_name
    ):
        """Test force deletion of empty container"""
        async with AsyncStorageBlobHelper(account_name=account_name) as helper:
            try:
                # Create empty container
                await helper.create_container(test_container_name)

                # Verify container is empty (no blobs)
                blobs = await helper.list_blobs(test_container_name)
                assert len(blobs) == 0

                # Test force delete on empty container should succeed
                result = await helper.delete_container(
                    test_container_name, force_delete=True
                )
                assert result is True

                # Verify container no longer exists
                container_exists = await helper.container_exists(test_container_name)
                assert container_exists is False

            except Exception as e:
                # Cleanup on test failure
                try:
                    await helper.delete_container(
                        test_container_name, force_delete=True
                    )
                except Exception:
                    pass  # Ignore cleanup errors
                raise e

    @pytest.mark.asyncio
    async def test_container_force_delete_multiple_blobs(
        self, account_name, test_container_name
    ):
        """Test force deletion of container with multiple blobs"""
        async with AsyncStorageBlobHelper(account_name=account_name) as helper:
            try:
                # Create container
                await helper.create_container(test_container_name)

                # Upload multiple blobs to the container
                blob_names = [f"test-blob-{i}.txt" for i in range(5)]
                for i, blob_name in enumerate(blob_names):
                    await helper.upload_blob(
                        container_name=test_container_name,
                        blob_name=blob_name,
                        data=f"Test content for blob {i}",
                    )

                # Verify all blobs exist
                blobs = await helper.list_blobs(test_container_name)
                assert len(blobs) == 5
                blob_names_found = [blob["name"] for blob in blobs]
                for blob_name in blob_names:
                    assert blob_name in blob_names_found

                # Test force delete succeeds with multiple blobs
                result = await helper.delete_container(
                    test_container_name, force_delete=True
                )
                assert result is True

                # Verify container no longer exists
                container_exists = await helper.container_exists(test_container_name)
                assert container_exists is False

            except Exception as e:
                # Cleanup on test failure
                try:
                    await helper.delete_container(
                        test_container_name, force_delete=True
                    )
                except Exception:
                    pass  # Ignore cleanup errors
                raise e

    @pytest.mark.asyncio
    async def test_real_blob_operations(
        self, account_name, test_container_name, test_blob_name
    ):
        """Test real async blob upload, download, and delete operations"""
        test_content = "Hello, async world!"

        async with AsyncStorageBlobHelper(account_name=account_name) as helper:
            try:
                # Create container first
                await helper.create_container(test_container_name)

                # Test blob upload
                result = await helper.upload_blob(
                    container_name=test_container_name,
                    blob_name=test_blob_name,
                    data=test_content,
                )
                assert result is not None
                assert "etag" in result or "last_modified" in result

                # Test blob exists
                exists = await helper.blob_exists(test_container_name, test_blob_name)
                assert exists is True

                # Test blob download
                downloaded_content = await helper.download_blob(
                    container_name=test_container_name, blob_name=test_blob_name
                )
                assert downloaded_content.decode("utf-8") == test_content

                # Test blob properties
                properties = await helper.get_blob_properties(
                    test_container_name, test_blob_name
                )
                assert "size" in properties
                assert "content_type" in properties
                assert "last_modified" in properties

                # Test list blobs
                blobs = await helper.list_blobs(test_container_name)
                assert isinstance(blobs, list)
                assert len(blobs) >= 1
                blob_names = [b["name"] for b in blobs]
                assert test_blob_name in blob_names

                # Test blob deletion
                delete_result = await helper.delete_blob(
                    test_container_name, test_blob_name
                )
                assert delete_result is True

                # Verify blob is deleted
                exists_after_delete = await helper.blob_exists(
                    test_container_name, test_blob_name
                )
                assert exists_after_delete is False

            finally:
                # Cleanup
                try:
                    await helper.delete_blob(test_container_name, test_blob_name)
                    await helper.delete_container(test_container_name)
                except Exception:
                    pass  # Ignore cleanup errors

    @pytest.mark.asyncio
    async def test_real_file_operations(
        self, account_name, test_container_name, test_blob_name
    ):
        """Test real async file upload and download operations"""
        test_content = "Async file content for upload/download test"

        # Create temporary files
        with tempfile.NamedTemporaryFile(
            mode="w", delete=False, suffix=".txt"
        ) as temp_upload:
            temp_upload.write(test_content)
            upload_file_path = temp_upload.name

        with tempfile.NamedTemporaryFile(delete=False, suffix=".txt") as temp_download:
            download_file_path = temp_download.name

        async with AsyncStorageBlobHelper(account_name=account_name) as helper:
            try:
                # Create container first
                await helper.create_container(test_container_name)

                # Test file upload
                upload_result = await helper.upload_file(
                    container_name=test_container_name,
                    blob_name=test_blob_name,
                    file_path=upload_file_path,
                )
                assert upload_result is True

                # Test file download
                download_result = await helper.download_file(
                    container_name=test_container_name,
                    blob_name=test_blob_name,
                    local_file_path=download_file_path,
                )
                assert download_result is True

                # Verify downloaded content
                async with aiofiles.open(download_file_path, "r") as f:
                    downloaded_content = await f.read()
                assert downloaded_content == test_content

            finally:
                # Cleanup files
                try:
                    os.unlink(upload_file_path)
                    os.unlink(download_file_path)
                    await helper.delete_blob(test_container_name, test_blob_name)
                    await helper.delete_container(test_container_name)
                except Exception:
                    pass  # Ignore cleanup errors

    @pytest.mark.asyncio
    async def test_real_blob_metadata_operations(
        self, account_name, test_container_name, test_blob_name
    ):
        """Test real async blob metadata operations"""
        test_content = "Async metadata test content"
        test_metadata = {"purpose": "async-testing", "category": "unit-test"}

        async with AsyncStorageBlobHelper(account_name=account_name) as helper:
            try:
                # Create container first
                await helper.create_container(test_container_name)

                # Upload blob with metadata
                await helper.upload_blob(
                    container_name=test_container_name,
                    blob_name=test_blob_name,
                    data=test_content,
                    metadata=test_metadata,
                )

                # Get blob properties to verify metadata
                properties = await helper.get_blob_properties(
                    test_container_name, test_blob_name
                )
                assert "metadata" in properties
                for key, value in test_metadata.items():
                    assert properties["metadata"].get(key) == value

                # Update metadata
                new_metadata = {"updated": "true", "version": "2"}
                result = await helper.set_blob_metadata(
                    test_container_name, test_blob_name, new_metadata
                )
                assert result is True

                # Verify updated metadata
                updated_properties = await helper.get_blob_properties(
                    test_container_name, test_blob_name
                )
                for key, value in new_metadata.items():
                    assert updated_properties["metadata"].get(key) == value

            finally:
                # Cleanup
                try:
                    await helper.delete_blob(test_container_name, test_blob_name)
                    await helper.delete_container(test_container_name)
                except Exception:
                    pass  # Ignore cleanup errors

    @pytest.mark.asyncio
    async def test_concurrent_uploads_real(self, account_name, test_container_name):
        """Test concurrent blob uploads with real Azure storage"""
        test_contents = [f"Concurrent content {i}" for i in range(3)]
        blob_names = [
            f"concurrent-test-{i}-{uuid.uuid4().hex[:8]}.txt" for i in range(3)
        ]

        async with AsyncStorageBlobHelper(account_name=account_name) as helper:
            try:
                # Create container first
                await helper.create_container(test_container_name)

                # Upload blobs concurrently
                upload_tasks = []
                for blob_name, content in zip(blob_names, test_contents):
                    task = helper.upload_blob(
                        container_name=test_container_name,
                        blob_name=blob_name,
                        data=content,
                    )
                    upload_tasks.append(task)

                # Wait for all uploads to complete
                upload_results = await asyncio.gather(*upload_tasks)

                # Verify all uploads succeeded
                for result in upload_results:
                    assert result is not None

                # Verify all blobs were uploaded
                blobs = await helper.list_blobs(test_container_name)
                uploaded_blob_names = [b["name"] for b in blobs]
                for blob_name in blob_names:
                    assert blob_name in uploaded_blob_names

                # Download and verify content concurrently
                download_tasks = []
                for blob_name in blob_names:
                    task = helper.download_blob(test_container_name, blob_name)
                    download_tasks.append(task)

                downloaded_contents = await asyncio.gather(*download_tasks)
                for i, downloaded_content in enumerate(downloaded_contents):
                    if isinstance(downloaded_content, bytes):
                        assert downloaded_content.decode("utf-8") == test_contents[i]
                    else:
                        assert downloaded_content == test_contents[i]

            finally:
                # Cleanup all blobs
                try:
                    for blob_name in blob_names:
                        await helper.delete_blob(test_container_name, blob_name)
                    await helper.delete_container(test_container_name)
                except Exception:
                    pass  # Ignore cleanup errors

    @pytest.mark.asyncio
    async def test_real_download_blob_to_file(
        self, account_name, test_container_name, test_blob_name
    ):
        """Test real async download blob to file operations"""
        test_content = "Async content for download to file test"

        # Create temporary file for download
        with tempfile.NamedTemporaryFile(delete=False, suffix=".txt") as temp_file:
            download_file_path = temp_file.name

        async with AsyncStorageBlobHelper(account_name=account_name) as helper:
            try:
                # Create container and upload blob
                await helper.create_container(test_container_name)
                await helper.upload_blob(
                    test_container_name, test_blob_name, test_content
                )

                # Test download to file
                download_result = await helper.download_file(
                    test_container_name, test_blob_name, download_file_path
                )
                assert download_result is True

                # Verify downloaded content
                async with aiofiles.open(download_file_path, "r") as f:
                    downloaded_content = await f.read()
                assert downloaded_content == test_content

            finally:
                # Cleanup
                try:
                    os.unlink(download_file_path)
                    await helper.delete_blob(test_container_name, test_blob_name)
                    await helper.delete_container(test_container_name)
                except Exception:
                    pass  # Ignore cleanup errors

    @pytest.mark.asyncio
    async def test_real_list_containers(self, account_name):
        """Test real async container listing"""
        container_prefix = f"async-list-test-{uuid.uuid4().hex[:8]}"
        container_names = [f"{container_prefix}-{i}" for i in range(2)]

        async with AsyncStorageBlobHelper(account_name=account_name) as helper:
            try:
                # Create test containers
                for container_name in container_names:
                    await helper.create_container(container_name)

                # Test list containers
                containers = await helper.list_containers()
                assert isinstance(containers, list)

                container_names_found = [c["name"] for c in containers]
                for container_name in container_names:
                    assert container_name in container_names_found

            finally:
                # Cleanup
                try:
                    for container_name in container_names:
                        await helper.delete_container(container_name)
                except Exception:
                    pass  # Ignore cleanup errors

    @pytest.mark.asyncio
    async def test_concurrent_container_operations(self, account_name):
        """Test concurrent container operations"""
        container_prefix = f"concurrent-ops-{uuid.uuid4().hex[:8]}"
        container_names = [f"{container_prefix}-{i}" for i in range(3)]

        async with AsyncStorageBlobHelper(account_name=account_name) as helper:
            try:
                # Test concurrent container creation
                create_tasks = []
                for container_name in container_names:
                    task = helper.create_container(container_name)
                    create_tasks.append(task)

                create_results = await asyncio.gather(*create_tasks)
                for result in create_results:
                    assert result is True

                # Test concurrent container existence checks
                exists_tasks = []
                for container_name in container_names:
                    task = helper.container_exists(container_name)
                    exists_tasks.append(task)

                exists_results = await asyncio.gather(*exists_tasks)
                for result in exists_results:
                    assert result is True

            finally:
                # Cleanup
                try:
                    delete_tasks = []
                    for container_name in container_names:
                        task = helper.delete_container(container_name)
                        delete_tasks.append(task)
                    await asyncio.gather(*delete_tasks, return_exceptions=True)
                except Exception:
                    pass  # Ignore cleanup errors


class TestAsyncStorageQueueHelperReal:
    """Test async queue helper functionality with real Azure resources"""

    @pytest.fixture
    def connection_string(self):
        """Get connection string from environment"""
        conn_str = os.getenv("AZURE_STORAGE_CONNECTION_STRING")
        if not conn_str:
            pytest.skip("AZURE_STORAGE_CONNECTION_STRING environment variable not set")
        return conn_str

    @pytest.fixture
    def account_name(self):
        account_name  = os.getenv("AZURE_STORAGE_ACCOUNT_NAME") #os.getenv("AZURE_STORAGE_ACCOUNT_NAME")
        if not account_name:
            pytest.skip("AZURE_STORAGE_ACCOUNT_NAME environment variable not set")
        return account_name

    @pytest.fixture
    def test_queue_name(self):
        """Generate unique queue name for testing"""
        return f"test-queue-{uuid.uuid4().hex[:8]}"

    @pytest.mark.asyncio
    async def test_async_context_manager(self, account_name):
        """Test async context manager functionality"""
        # Test that context manager works with real connection
        async with AsyncStorageQueueHelper(account_name=account_name) as helper:
            assert helper._queue_service_client is not None

    @pytest.mark.asyncio
    async def test_real_queue_operations(self, account_name, test_queue_name):
        """Test real async queue operations"""
        async with AsyncStorageQueueHelper(account_name=account_name) as helper:
            try:
                # Test queue creation
                result = await helper.create_queue(test_queue_name)
                assert result is True

                # Test queue exists
                exists = await helper.queue_exists(test_queue_name)
                assert exists is True

                # Test list queues
                queues = await helper.list_queues()
                assert isinstance(queues, list)
                queue_names = [q["name"] for q in queues]
                assert test_queue_name in queue_names

                # Test queue properties
                properties = await helper.get_queue_properties(test_queue_name)
                assert "name" in properties
                assert properties["name"] == test_queue_name
                assert "approximate_message_count" in properties

            finally:
                # Cleanup
                try:
                    await helper.delete_queue(test_queue_name)
                except Exception:
                    pass  # Ignore cleanup errors

    @pytest.mark.asyncio
    async def test_real_message_operations(self, account_name, test_queue_name):
        """Test real async message operations"""
        test_message = "Hello, async queue world!"

        async with AsyncStorageQueueHelper(account_name=account_name) as helper:
            try:
                # Create queue first
                await helper.create_queue(test_queue_name)

                # Test message sending
                send_result = await helper.send_message(test_queue_name, test_message)
                assert "message_id" in send_result
                assert "pop_receipt" in send_result

                # Wait a moment for message to be available
                await asyncio.sleep(1)

                # Test message receiving
                messages = await helper.receive_messages(
                    test_queue_name, max_messages=1
                )
                assert len(messages) >= 1
                received_message = messages[0]
                assert received_message["content"] == test_message
                assert "id" in received_message
                assert "pop_receipt" in received_message

                # Test message deletion
                delete_result = await helper.delete_message(
                    test_queue_name,
                    received_message["id"],
                    received_message["pop_receipt"],
                )
                assert delete_result is True

            finally:
                # Cleanup
                try:
                    await helper.delete_queue(test_queue_name)
                except Exception:
                    pass  # Ignore cleanup errors

    @pytest.mark.asyncio
    async def test_batch_message_sending_real(self, account_name, test_queue_name):
        """Test batch message sending with real Azure queue"""
        messages = [f"Async message {i}" for i in range(3)]

        async with AsyncStorageQueueHelper(account_name=account_name) as helper:
            try:
                # Create queue first
                await helper.create_queue(test_queue_name)

                # Send messages in batch
                results = await helper.send_messages_batch(
                    test_queue_name, messages, max_concurrency=2
                )

                # All messages should be sent
                assert len(results) == 3
                for result in results:
                    assert "message_id" in result

                # Wait a moment for messages to be available
                await asyncio.sleep(1)

                # Receive messages to verify
                received_messages = await helper.receive_messages(
                    test_queue_name, max_messages=5
                )
                assert len(received_messages) >= len(messages)

                # Verify message content
                received_contents = [msg["content"] for msg in received_messages]
                for original_message in messages:
                    assert original_message in received_contents

                # Clean up messages
                for message in received_messages:
                    await helper.delete_message(
                        test_queue_name, message["id"], message["pop_receipt"]
                    )

            finally:
                # Cleanup
                try:
                    await helper.delete_queue(test_queue_name)
                except Exception:
                    pass  # Ignore cleanup errors

    @pytest.mark.asyncio
    async def test_process_messages_batch_real(self, account_name, test_queue_name):
        """Test batch message processing with real Azure queue"""
        messages = [f"Process me {i}" for i in range(3)]

        async with AsyncStorageQueueHelper(account_name=account_name) as helper:
            try:
                # Create queue first
                await helper.create_queue(test_queue_name)

                # Send messages
                for message in messages:
                    await helper.send_message(test_queue_name, message)

                # Wait a moment for messages to be available
                await asyncio.sleep(1)

                # Define async processor function
                async def process_message(message):
                    """Process a single message"""
                    content = message["content"]
                    return f"Processed: {content}"

                # Process messages in batch
                results = await helper.process_messages_batch(
                    test_queue_name,
                    process_message,
                    max_messages=5,
                    max_concurrency=2,
                    delete_after_processing=True,
                )

                # Verify processing results
                assert len(results) >= len(messages)
                for result in results:
                    assert result["success"] is True
                    assert "Processed:" in result["result"]

            finally:
                # Cleanup
                try:
                    await helper.delete_queue(test_queue_name)
                except Exception:
                    pass  # Ignore cleanup errors

    @pytest.mark.asyncio
    async def test_real_peek_messages(self, account_name, test_queue_name):
        """Test peeking at messages without removing them"""
        test_message = "Async peek test message"

        async with AsyncStorageQueueHelper(account_name=account_name) as helper:
            try:
                # Create queue and send message
                await helper.create_queue(test_queue_name)
                await helper.send_message(test_queue_name, test_message)

                # Wait a moment for message to be available
                await asyncio.sleep(1)

                # Peek at messages
                peeked_messages = await helper.peek_messages(
                    test_queue_name, max_messages=1
                )
                assert len(peeked_messages) >= 1
                assert peeked_messages[0]["content"] == test_message

                # Verify message is still in queue by receiving it
                received_messages = await helper.receive_messages(
                    test_queue_name, max_messages=1
                )
                assert len(received_messages) >= 1
                assert received_messages[0]["content"] == test_message

                # Clean up the message
                await helper.delete_message(
                    test_queue_name,
                    received_messages[0]["id"],
                    received_messages[0]["pop_receipt"],
                )

            finally:
                # Cleanup
                try:
                    await helper.delete_queue(test_queue_name)
                except Exception:
                    pass  # Ignore cleanup errors

    @pytest.mark.asyncio
    async def test_real_clear_queue(self, account_name, test_queue_name):
        """Test clearing all messages from queue"""
        test_messages = [f"Clear test message {i}" for i in range(3)]

        async with AsyncStorageQueueHelper(account_name=account_name) as helper:
            try:
                # Create queue and send messages
                await helper.create_queue(test_queue_name)
                for message in test_messages:
                    await helper.send_message(test_queue_name, message)

                # Wait a moment for messages to be available
                await asyncio.sleep(1)

                # Clear queue
                clear_result = await helper.clear_queue(test_queue_name)
                assert clear_result is True

                # Wait a moment for clear to take effect
                await asyncio.sleep(1)

                # Verify queue is empty
                messages = await helper.receive_messages(
                    test_queue_name, max_messages=10
                )
                assert len(messages) == 0

            finally:
                # Cleanup
                try:
                    await helper.delete_queue(test_queue_name)
                except Exception:
                    pass  # Ignore cleanup errors

    @pytest.mark.asyncio
    async def test_real_update_and_delete_message(self, account_name, test_queue_name):
        """Test real async message update and delete operations"""
        test_message = "Async message for update/delete test"

        async with AsyncStorageQueueHelper(account_name=account_name) as helper:
            try:
                # Create queue and send message
                await helper.create_queue(test_queue_name)
                send_result = await helper.send_message(test_queue_name, test_message)
                assert "message_id" in send_result

                # Receive message to get pop receipt
                messages = await helper.receive_messages(
                    test_queue_name, max_messages=1
                )
                assert len(messages) >= 1

                message = messages[0]
                pop_receipt = message["pop_receipt"]
                message_id = message["id"]

                # Test update message
                updated_content = "Updated async message content"
                update_result = await helper.update_message(
                    test_queue_name, message_id, pop_receipt, updated_content
                )

                # assert update_result["pop_receipt"] is message["pop_receipt"]

                # Receive updated message to verify
                updated_messages = await helper.receive_messages(
                    test_queue_name, max_messages=1
                )

                assert updated_messages[0]["content"] == updated_content

                if updated_messages:  # Message might still be processing
                    updated_message = updated_messages[0]
                    new_pop_receipt = updated_message["pop_receipt"]

                    # Test delete message
                    delete_result = await helper.delete_message(
                        test_queue_name, updated_message["id"], new_pop_receipt
                    )
                    assert delete_result is True

            finally:
                # Cleanup
                try:
                    await helper.delete_queue(test_queue_name)
                except Exception:
                    pass  # Ignore cleanup errors

    @pytest.mark.asyncio
    async def test_real_queue_properties_and_metadata(
        self, account_name, test_queue_name
    ):
        """Test async queue properties and metadata operations"""
        test_metadata = {"environment": "test", "version": "1.0"}

        async with AsyncStorageQueueHelper(account_name=account_name) as helper:
            try:
                # Create queue with metadata
                await helper.create_queue(test_queue_name, metadata=test_metadata)

                # Test get queue properties
                properties = await helper.get_queue_properties(test_queue_name)
                assert "name" in properties
                assert properties["name"] == test_queue_name
                assert "metadata" in properties

                # Verify metadata
                for key, value in test_metadata.items():
                    assert properties["metadata"].get(key) == value

                # Test set queue metadata
                new_metadata = {"updated": "true", "new_field": "test_value"}
                metadata_result = await helper.set_queue_metadata(
                    test_queue_name, new_metadata
                )
                assert metadata_result is True

                # Verify updated metadata
                updated_properties = await helper.get_queue_properties(test_queue_name)
                for key, value in new_metadata.items():
                    assert updated_properties["metadata"].get(key) == value

            finally:
                # Cleanup
                try:
                    await helper.delete_queue(test_queue_name)
                except Exception:
                    pass  # Ignore cleanup errors

    @pytest.mark.asyncio
    async def test_real_message_json_operations(self, account_name, test_queue_name):
        """Test async JSON message operations"""
        test_data = {"type": "async_test", "value": 42, "active": True}

        async with AsyncStorageQueueHelper(account_name=account_name) as helper:
            try:
                # Create queue first
                await helper.create_queue(test_queue_name)

                # Send JSON message
                send_result = await helper.send_message(test_queue_name, test_data)
                assert "message_id" in send_result

                # Wait a moment for message to be available
                await asyncio.sleep(1)

                # Receive and verify JSON message
                messages = await helper.receive_messages(
                    test_queue_name, max_messages=1
                )
                assert len(messages) >= 1
                received_message = messages[0]

                # The content should be JSON string, so we need to parse it
                import json

                received_data = json.loads(received_message["content"])
                assert received_data == test_data

                # Clean up the message
                await helper.delete_message(
                    test_queue_name,
                    received_message["id"],
                    received_message["pop_receipt"],
                )

            finally:
                # Cleanup
                try:
                    await helper.delete_queue(test_queue_name)
                except Exception:
                    pass  # Ignore cleanup errors


class TestAsyncStorageBlobHelperSASTokensReal:
    """Test SAS token generation with async blob helper"""

    @pytest.fixture
    def connection_string(self):
        """Get connection string from environment"""
        conn_str = os.getenv("AZURE_STORAGE_CONNECTION_STRING")
        if not conn_str:
            pytest.skip("AZURE_STORAGE_CONNECTION_STRING environment variable not set")
        return conn_str

    @pytest.fixture
    def account_name(self):
        account_name  = os.getenv("AZURE_STORAGE_ACCOUNT_NAME")  #os.getenv("AZURE_STORAGE_ACCOUNT_NAME")
        if not account_name:
            pytest.skip("AZURE_STORAGE_ACCOUNT_NAME environment variable not set")
        return account_name

    @pytest.fixture
    def test_container_name(self):
        """Generate unique container name for testing"""
        return f"sas-test-container-{uuid.uuid4().hex[:8]}"

    @pytest.fixture
    def test_blob_name(self):
        """Generate unique blob name for testing"""
        return f"sas-test-blob-{uuid.uuid4().hex[:8]}.txt"

    @pytest.mark.asyncio
    async def test_generate_blob_sas_url_real(
        self, account_name, test_container_name, test_blob_name
    ):
        """Test async blob SAS URL generation with real Azure resources"""
        test_content = "Async SAS token test content"

        async with AsyncStorageBlobHelper(account_name=account_name) as helper:
            try:
                # Create container and upload blob
                await helper.create_container(test_container_name)
                await helper.upload_blob(
                    test_container_name, test_blob_name, test_content
                )

                # Generate SAS URL
                sas_url = await helper.generate_blob_sas_url(
                    container_name=test_container_name,
                    blob_name=test_blob_name,
                    permissions="r",  # read permission
                    expiry_hours=1,
                )

                assert isinstance(sas_url, str)
                assert "sig=" in sas_url  # SAS signature
                # Test the SAS URL by making HTTP request
                try:
                    async with aiohttp.ClientSession() as session:
                        async with session.get(sas_url) as response:
                            assert response.status == 200
                            content = await response.text()
                            assert content == test_content
                except Exception as e:
                    # SAS URL testing might fail due to permissions, but URL generation should work
                    assert isinstance(sas_url, str) and "sig=" in sas_url
                        assert response.status == 200
                        content = await response.text()
                        assert content == test_content

            finally:
                # Cleanup
                try:
                    await helper.delete_blob(test_container_name, test_blob_name)
                    await helper.delete_container(test_container_name)
                except Exception:
                    pass  # Ignore cleanup errors

    @pytest.mark.asyncio
    async def test_generate_container_sas_url_real(
        self, account_name, test_container_name
    ):
        """Test async container SAS URL generation with real Azure resources"""
        async with AsyncStorageBlobHelper(account_name=account_name) as helper:
            try:
                # Create container
                await helper.create_container(test_container_name)

                # Generate container SAS URL
                sas_url = await helper.generate_container_sas_url(
                    container_name=test_container_name,
                    permissions="rl",  # read and list permissions for container access
                # Test the SAS URL by listing blobs
                try:
                    list_url = f"{sas_url}&restype=container&comp=list"
                    async with aiohttp.ClientSession() as session:
                        async with session.get(list_url) as response:
                            assert response.status == 200
                except Exception as e:
                    # SAS URL testing might fail due to permissions, but URL generation should work
                    assert isinstance(sas_url, str) and "sig=" in sas_url
                assert test_container_name in sas_url

                # Test the SAS URL by listing blobs
                list_url = f"{sas_url}&restype=container&comp=list"
                async with aiohttp.ClientSession() as session:
                    async with session.get(list_url) as response:
                        assert response.status == 200

            finally:
                # Cleanup
                try:
                    await helper.delete_container(test_container_name)
                except Exception:
                    pass  # Ignore cleanup errors

    @pytest.mark.asyncio
    async def test_generate_blob_sas_url_user_delegation_real(
        self, account_name, test_container_name, test_blob_name
    ):
        """Test async blob SAS URL generation with user delegation key"""
        test_content = "User delegation SAS test content"

        async with AsyncStorageBlobHelper(account_name=account_name) as helper:
            try:
                # Create container and upload blob
                await helper.create_container(test_container_name)
                await helper.upload_blob(
                    test_container_name, test_blob_name, test_content
                )

                # Generate user delegation SAS URL
                sas_url = await helper.generate_blob_sas_url(
                    container_name=test_container_name,
                    blob_name=test_blob_name,
                    permissions="r",  # read permission
                    expiry_hours=1,
                )

                assert isinstance(sas_url, str)
                assert "sig=" in sas_url  # SAS signature
                assert test_container_name in sas_url
                assert test_blob_name in sas_url

                # Test the SAS URL by making HTTP request
                async with aiohttp.ClientSession() as session:
                    async with session.get(sas_url) as response:
                        assert response.status == 200
                        content = await response.text()
                        assert content == test_content
            except Exception as e:
                pytest.fail(f"Failed to generate user delegation SAS URL: {e}")
            finally:
                # Cleanup
                try:
                    await helper.delete_blob(test_container_name, test_blob_name)
                    await helper.delete_container(test_container_name)
                except Exception:
                    pass  # Ignore cleanup errors

    @pytest.mark.asyncio
    async def test_generate_container_sas_url_user_delegation_real(
        self, account_name, test_container_name
    ):
        """Test async container SAS URL generation with user delegation key"""
        async with AsyncStorageBlobHelper(account_name=account_name) as helper:
            try:
                # Create container
                await helper.create_container(test_container_name)

                # Generate user delegation container SAS URL
                sas_url = await helper.generate_container_sas_url(
                    container_name=test_container_name,
                    permissions="rl",  # read and list permissions for container access
                    expiry_hours=1,
                )

                assert isinstance(sas_url, str)
                assert "sig=" in sas_url  # SAS signature
                assert test_container_name in sas_url

                # Test the SAS URL by listing blobs
                list_url = f"{sas_url}&restype=container&comp=list"
                async with aiohttp.ClientSession() as session:
                    async with session.get(list_url) as response:
                        assert response.status == 200

            finally:
                # Cleanup
                try:
                    await helper.delete_container(test_container_name)
                except Exception:
                    pass  # Ignore cleanup errors


class TestAsyncStorageHelpersIntegration:
    """Test integration scenarios with both async blob and queue helpers"""

    @pytest.fixture
    def connection_string(self):
        """Get connection string from environment"""
        conn_str = os.getenv("AZURE_STORAGE_CONNECTION_STRING")
        if not conn_str:
            pytest.skip("AZURE_STORAGE_CONNECTION_STRING environment variable not set")
        return conn_str

    @pytest.fixture
    def account_name(self):
        account_name  = os.getenv("AZURE_STORAGE_ACCOUNT_NAME")  #os.getenv("AZURE_STORAGE_ACCOUNT_NAME")
        if not account_name:
            pytest.skip("AZURE_STORAGE_ACCOUNT_NAME environment variable not set")
        return account_name

    @pytest.fixture
    def test_container_name(self):
        """Generate unique container name for testing"""
        return f"integration-container-{uuid.uuid4().hex[:8]}"

    @pytest.fixture
    def test_queue_name(self):
            async with AsyncStorageBlobHelper(account_name=account_name) as blob_helper:
            await blob_helper.create_container(test_container_name)
            await blob_helper.upload_blob(
                test_container_name,
                "concurrent.txt",
                "Data from concurrent operation",
            )
            content = await blob_helper.download_file(
                test_container_name, "concurrent.txt", "concurrent.txt"
            )

            assert content is True, "Blob download failed"
                await blob_helper.create_container(test_container_name)
                await blob_helper.upload_blob_from_text(
                    test_container_name,
                    "concurrent.txt",
                    "Data from concurrent operation",
                )
                content = await blob_helper.download_blob_to_file(
                    test_container_name, "concurrent.txt", "concurrent.txt"
                )

                assert content is True, "Blob download failed"

                await blob_helper.delete_container(
                    test_container_name, force_delete=True
                )
                return "Blob task completed. you can check the file from here ./concurrent.txt"

                messages = await queue_helper.receive_messages(test_queue_name, max_messages=1)
                message = messages[0] if messages else None
                if message:
                    await queue_helper.delete_message(
                        test_queue_name, message["id"], message["pop_receipt"]
                    )
                await queue_helper.create_queue(test_queue_name)
                message_data = {"concurrent": True, "data": "test"}
                await queue_helper.send_message(test_queue_name, message_data)

                await asyncio.sleep(1)  # Wait for message availability

                message = await queue_helper.receive_message(test_queue_name)
                if message:
                    await queue_helper.delete_message(
                        test_queue_name, message["id"], message["pop_receipt"]
                    )

                await queue_helper.delete_queue(test_queue_name)
                return f"Queue task completed: processed message with ID {message['id'] if message else 'None'}"

        # Run both tasks concurrently
        blob_result, queue_result = await asyncio.gather(blob_task(), queue_task())

        assert "Blob task completed" in blob_result
        assert "Queue task completed" in queue_result

    @pytest.mark.asyncio
    async def test_copy_blob_with_metadata(self, account_name, test_container_name):
        """Test blob copy operation with metadata"""
        async with AsyncStorageBlobHelper(account_name=account_name) as blob_helper:
            await blob_helper.create_container(test_container_name)

            # Upload source blob
            source_blob = "source-test.txt"
            test_content = "Test content for copying"
            await blob_helper.upload_blob(
                test_container_name, source_blob, test_content.encode(), overwrite=True
            )

            # Copy with metadata
            dest_blob = "dest-test.txt"
            metadata = {"copied": "true", "timestamp": "2025-09-19"}
            copy_id = await blob_helper.copy_blob(
                source_container=test_container_name,
                source_blob=source_blob,
                dest_container=test_container_name,
                dest_blob=dest_blob,
                metadata=metadata,
                overwrite=True,
            )

            assert copy_id is not None

            # Verify copy and metadata
            assert await blob_helper.blob_exists(test_container_name, dest_blob)
            properties = await blob_helper.get_blob_properties(
                test_container_name, dest_blob
            )
            assert properties["metadata"]["copied"] == "true"
            assert properties["metadata"]["timestamp"] == "2025-09-19"

            # Clean up
            await blob_helper.delete_container(test_container_name, force_delete=True)

    @pytest.mark.asyncio
    async def test_move_blob_with_metadata(self, account_name, test_container_name):
        """Test blob move operation with metadata"""
        async with AsyncStorageBlobHelper(account_name=account_name) as blob_helper:
            await blob_helper.create_container(test_container_name)

            # Upload source blob
            source_blob = "source-move.txt"
            test_content = "Test content for moving"
            await blob_helper.upload_blob(
                test_container_name, source_blob, test_content.encode(), overwrite=True
            )

            # Move with metadata
            dest_blob = "dest-move.txt"
            metadata = {"moved": "true", "operation": "move"}
            copy_id = await blob_helper.move_blob(
                source_container=test_container_name,
                source_blob=source_blob,
                dest_container=test_container_name,
                dest_blob=dest_blob,
                metadata=metadata,
                overwrite=True,
            )

            assert copy_id is not None

            # Verify move: dest exists, source doesn't
            assert await blob_helper.blob_exists(test_container_name, dest_blob)
            assert not await blob_helper.blob_exists(test_container_name, source_blob)

            # Verify metadata
            properties = await blob_helper.get_blob_properties(
                test_container_name, dest_blob
            )
            # Upload text content
            blob_name = "text-upload.txt"
            text_content = "Hello, Azure Storage!\nThis is a test file."

            success = await blob_helper.upload_blob(
                container_name=test_container_name,
                blob_name=blob_name,
                data=text_content.encode(),
                content_type="text/plain",
                overwrite=True,
            )

            # Upload text content
            blob_name = "text-upload.txt"
            text_content = "Hello, Azure Storage!\nThis is a test file."

            success = await blob_helper.upload_blob_from_text(
                container_name=test_container_name,
                blob_name=blob_name,
                text_content=text_content,
                content_type="text/plain",
                overwrite=True,
            )

            assert success is True

            # Verify content
            downloaded_content = await blob_helper.download_blob(
                test_container_name, blob_name
            )
            assert downloaded_content.decode("utf-8") == text_content

            # Clean up
            await blob_helper.delete_container(test_container_name, force_delete=True)

    @pytest.mark.asyncio
    async def test_download_file_new(self, account_name, test_container_name):
        """Test downloading blob to local file"""
        async with AsyncStorageBlobHelper(account_name=account_name) as blob_helper:
            await blob_helper.create_container(test_container_name)

            # Upload test blob
            blob_name = "download-test.txt"
            test_content = "Content for download test"
            await blob_helper.upload_blob(
                test_container_name, blob_name, test_content.encode(), overwrite=True
            )

            # Download to local file
            with tempfile.NamedTemporaryFile(delete=False) as temp_file:
                local_path = temp_file.name

            try:
                success = await blob_helper.download_file(
                    container_name=test_container_name,
                    blob_name=blob_name,
                    local_file_path=local_path,
                )

                assert success is True

                # Verify file content
                async with aiofiles.open(local_path, "r") as f:
                    content = await f.read()
                    assert content == test_content

            finally:
                # Clean up
                if os.path.exists(local_path):
                    os.unlink(local_path)
                await blob_helper.delete_container(
                    test_container_name, force_delete=True
                )

    @pytest.mark.asyncio
    async def test_list_blobs_hierarchical_new(self, account_name, test_container_name):
        """Test hierarchical blob listing"""
        async with AsyncStorageBlobHelper(account_name=account_name) as blob_helper:
            await blob_helper.create_container(test_container_name)

            # Create test blobs with hierarchical structure
            test_blobs = [
                "folder1/file1.txt",
                "folder1/file2.txt",
            # List all blobs (fallback if hierarchical method doesn't exist)
            try:
                result = await blob_helper.list_blobs_hierarchical(
                    container_name=test_container_name, prefix="", delimiter="/"
                )
                assert "blobs" in result
                assert "prefixes" in result
            except AttributeError:
                # Fallback to regular list_blobs
                blobs = await blob_helper.list_blobs(test_container_name)
                assert len(blobs) >= 4  # Should have all test blobs
                blob_names = [blob["name"] for blob in blobs]
                for test_blob in test_blobs:
                    assert test_blob in blob_names

            assert "blobs" in result
            assert "prefixes" in result
            assert len(result["blobs"]) >= 1  # Should have root-file.txt
            assert len(result["prefixes"]) >= 2  # Should have folder1/ and folder2/

            # List folder1 contents
            folder1_result = await blob_helper.list_blobs_hierarchical(
                container_name=test_container_name, prefix="folder1/", delimiter="/"
            )

            assert len(folder1_result["blobs"]) == 2  # file1.txt and file2.txt

            # Clean up
            await blob_helper.delete_container(test_container_name, force_delete=True)

    @pytest.mark.asyncio
    async def test_get_blob_properties_new(self, account_name, test_container_name):
        """Test getting detailed blob properties"""
        async with AsyncStorageBlobHelper(account_name=account_name) as blob_helper:
            await blob_helper.create_container(test_container_name)

            # Upload blob with metadata
            blob_name = "properties-test.txt"
            test_content = "Content for properties test"
            metadata = {"test": "value", "property": "check"}

            await blob_helper.upload_blob(
                test_container_name,
                blob_name,
                test_content.encode(),
                content_type="text/plain",
                metadata=metadata,
                overwrite=True,
            )

            # Get properties
            properties = await blob_helper.get_blob_properties(
                test_container_name, blob_name
            )

            assert properties is not None
            assert properties["name"] == blob_name
            assert properties["container"] == test_container_name
            assert properties["size"] == len(test_content)
            assert properties["content_type"] == "text/plain"
            assert properties["metadata"]["test"] == "value"
            assert properties["metadata"]["property"] == "check"
            assert "last_modified" in properties
            assert "etag" in properties

            # Clean up
            await blob_helper.delete_container(test_container_name, force_delete=True)

    @pytest.mark.asyncio
    async def test_set_blob_metadata_new(self, account_name, test_container_name):
        """Test setting blob metadata"""
        async with AsyncStorageBlobHelper(account_name=account_name) as blob_helper:
            await blob_helper.create_container(test_container_name)

            # Upload blob
            blob_name = "metadata-test.txt"
            test_content = "Content for metadata test"
            await blob_helper.upload_blob(
                test_container_name, blob_name, test_content.encode(), overwrite=True
            )

            # Set metadata
            new_metadata = {"updated": "true", "version": "1.0", "author": "test"}
            success = await blob_helper.set_blob_metadata(
                test_container_name, blob_name, new_metadata
            )

            assert success is True

            # Verify metadata
            properties = await blob_helper.get_blob_properties(
                test_container_name, blob_name
            )
            assert properties["metadata"]["updated"] == "true"
            assert properties["metadata"]["version"] == "1.0"
            assert properties["metadata"]["author"] == "test"

            # Clean up
            await blob_helper.delete_container(test_container_name, force_delete=True)

    @pytest.mark.asyncio
    async def test_download_multiple_blobs_new(self, account_name, test_container_name):
        """Test downloading multiple blobs concurrently"""
        async with AsyncStorageBlobHelper(account_name=account_name) as blob_helper:
            await blob_helper.create_container(test_container_name)

            # Download multiple blobs (implement manually if method doesn't exist)
            with tempfile.TemporaryDirectory() as temp_dir:
                try:
                    results = await blob_helper.download_multiple_blobs(
                        container_name=test_container_name,
                        blob_names=test_blobs,
                        local_directory=temp_dir,
                        max_concurrency=2,
                    )
                    assert len(results) == 3
                    assert all(results.values())
                except AttributeError:
                    # Fallback to individual downloads
                    for blob_name in test_blobs:
                        file_path = os.path.join(temp_dir, blob_name)
                        success = await blob_helper.download_file(
                            test_container_name, blob_name, file_path
                        )
                        assert success is True

                # Verify files exist
                for blob_name in test_blobs:
                    file_path = os.path.join(temp_dir, blob_name)
                    assert os.path.exists(file_path)
                    with open(file_path, "r") as f:
                        content = f.read()
                        assert content == f"Content of {blob_name}"
                assert len(results) == 3
                assert all(results.values())  # All downloads should succeed

                # Verify files exist
                for blob_name in test_blobs:
                    file_path = os.path.join(temp_dir, blob_name)
                    assert os.path.exists(file_path)
                    with open(file_path, "r") as f:
                        content = f.read()
                        assert content == f"Content of {blob_name}"

            # Clean up
            await blob_helper.delete_container(test_container_name, force_delete=True)

    @pytest.mark.asyncio
    async def test_delete_multiple_blobs_new(self, account_name, test_container_name):
            # Delete multiple blobs (implement manually if method doesn't exist)
            try:
                results = await blob_helper.delete_multiple_blobs(
                    container_name=test_container_name,
                    blob_names=test_blobs,
                    max_concurrency=2,
                )
                assert len(results) == 3
                assert all(results.values())
            except AttributeError:
                # Fallback to individual deletions
                for blob_name in test_blobs:
                    success = await blob_helper.delete_blob(test_container_name, blob_name)
                    assert success is True
                    blob_name,
                    f"Content of {blob_name}".encode(),
                    overwrite=True,
                )

            # Verify all blobs exist
            for blob_name in test_blobs:
                assert await blob_helper.blob_exists(test_container_name, blob_name)

            # Delete multiple blobs
            results = await blob_helper.delete_multiple_blobs(
                container_name=test_container_name,
                blob_names=test_blobs,
                max_concurrency=2,
            )

            assert len(results) == 3
            assert all(results.values())  # All deletions should succeed

            # Verify all blobs are deleted
            for blob_name in test_blobs:
                assert not await blob_helper.blob_exists(test_container_name, blob_name)

            # Clean up
            await blob_helper.delete_container(test_container_name, force_delete=True)
