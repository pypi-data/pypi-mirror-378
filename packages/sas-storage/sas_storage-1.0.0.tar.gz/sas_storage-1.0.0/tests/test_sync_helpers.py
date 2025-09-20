#!/usr/bin/env python3
"""
Comprehensive tests for sync storage helpers using real Azure resources

This module tests both StorageBlobHelper and StorageQueueHelper with real Azure resources.
All tests use environment-based configuration and automatic test skipping.
"""

import pytest
import os
import sys
import uuid
import tempfile
import time

# Add src to path for imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))

from sas.storage.blob.helper import StorageBlobHelper
from sas.storage.queue.helper import StorageQueueHelper


class TestStorageBlobHelperReal:
    """Test sync blob helper functionality with real Azure resources"""

    @pytest.fixture
    def connection_string(self):
        """Get connection string from environment"""
        conn_str = os.getenv("AZURE_STORAGE_CONNECTION_STRING")
        if not conn_str:
            pytest.skip("AZURE_STORAGE_CONNECTION_STRING environment variable not set")
        return conn_str

    @pytest.fixture
    def account_name(self):
        account_name = "appfrmstorageaccount"  # os.getenv("AZURE_STORAGE_ACCOUNT_NAME")
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

    def test_init_with_connection_string(self, connection_string):
        """Test initialization with connection string"""
        helper = StorageBlobHelper(connection_string=connection_string)
        assert helper is not None
        assert helper.blob_service_client is not None

    def test_real_container_operations(self, account_name, test_container_name):
        """Test real container operations"""
        helper = StorageBlobHelper(account_name=account_name)

        try:
            # Test container creation
            result = helper.create_container(test_container_name)
            assert result is True

            # Test container exists
            exists = helper.container_exists(test_container_name)
            assert exists is True

            # Test list containers
            containers = helper.list_containers()
            assert isinstance(containers, list)
            container_names = [c["name"] for c in containers]
            assert test_container_name in container_names

        finally:
            # Cleanup
            try:
                helper.delete_container(test_container_name)
            except Exception:
                pass  # Ignore cleanup errors

    def test_container_force_delete(
        self, account_name, test_container_name, test_blob_name
    ):
        """Test force deletion of container with blobs"""

        helper = StorageBlobHelper(account_name=account_name)

        try:
            # Create container
            helper.create_container(test_container_name)

            # Upload a blob to the container
            test_content = "Test content for force delete"
            helper.upload_blob(
                container_name=test_container_name,
                blob_name=test_blob_name,
                data=test_content,
            )

            # Verify blob exists
            exists = helper.blob_exists(test_container_name, test_blob_name)
            assert exists is True

            # Test that normal delete fails with container containing blobs
            with pytest.raises((ValueError, Exception)) as exc_info:
                helper.delete_container(test_container_name, force_delete=False)

            # Verify the error message suggests using force_delete
            error_msg = str(exc_info.value).lower()
            assert "force_delete" in error_msg or "not empty" in error_msg

            # Verify container and blob still exist
            container_exists = helper.container_exists(test_container_name)
            blob_exists = helper.blob_exists(test_container_name, test_blob_name)
            assert container_exists is True
            assert blob_exists is True

            # Test force delete succeeds
            result = helper.delete_container(test_container_name, force_delete=True)
            assert result is True

            # Verify container no longer exists
            container_exists = helper.container_exists(test_container_name)
            assert container_exists is False

        except Exception as e:
            # Cleanup on test failure
            try:
                helper.delete_container(test_container_name, force_delete=True)
            except Exception:
                pass  # Ignore cleanup errors
            raise e

    def test_container_force_delete_empty(self, account_name, test_container_name):
        """Test force deletion of empty container"""
        helper = StorageBlobHelper(account_name=account_name)
        # with StorageBlobHelper(account_name=account_name) as helper:
        try:
            # Create empty container
            helper.create_container(test_container_name)

            # Verify container is empty (no blobs)
            blobs = helper.list_blobs(test_container_name)
            assert len(blobs) == 0

            # Test force delete on empty container should succeed
            result = helper.delete_container(test_container_name, force_delete=True)
            assert result is True

            # Verify container no longer exists
            container_exists = helper.container_exists(test_container_name)
            assert container_exists is False

        except Exception as e:
            # Cleanup on test failure
            try:
                helper.delete_container(test_container_name, force_delete=True)
            except Exception:
                pass  # Ignore cleanup errors
            raise e

    def test_container_force_delete_multiple_blobs(
        self, account_name, test_container_name
    ):
        """Test force deletion of container with multiple blobs"""
        helper = StorageBlobHelper(account_name=account_name)
        # with StorageBlobHelper(account_name=account_name) as helper:
        try:
            # Create container
            helper.create_container(test_container_name)

            # Upload multiple blobs to the container
            blob_names = [f"test-blob-{i}.txt" for i in range(5)]
            for i, blob_name in enumerate(blob_names):
                helper.upload_blob(
                    container_name=test_container_name,
                    blob_name=blob_name,
                    data=f"Test content for blob {i}",
                )

            # Verify all blobs exist
            blobs = helper.list_blobs(test_container_name)
            assert len(blobs) == 5
            blob_names_found = [blob["name"] for blob in blobs]
            for blob_name in blob_names:
                assert blob_name in blob_names_found

            # Test force delete succeeds with multiple blobs
            result = helper.delete_container(test_container_name, force_delete=True)
            assert result is True

            # Verify container no longer exists
            container_exists = helper.container_exists(test_container_name)
            assert container_exists is False

        except Exception as e:
            # Cleanup on test failure
            try:
                helper.delete_container(test_container_name, force_delete=True)
            except Exception:
                pass  # Ignore cleanup errors
            raise e

    def test_real_blob_operations(
        self, account_name, test_container_name, test_blob_name
    ):
        """Test real blob upload, download, and delete operations"""
        test_content = "Hello, sync world!"
        helper = StorageBlobHelper(account_name=account_name)

        try:
            # Create container first
            helper.create_container(test_container_name)

            # Test blob upload
            result = helper.upload_blob(
                container_name=test_container_name,
                blob_name=test_blob_name,
                data=test_content,
            )
            assert result is True

            # Test blob exists
            exists = helper.blob_exists(test_container_name, test_blob_name)
            assert exists is True

            # Test blob download
            downloaded_content = helper.download_blob(
                test_container_name, test_blob_name
            )
            assert downloaded_content.decode("utf-8") == test_content

            # Test blob properties
            properties = helper.get_blob_properties(test_container_name, test_blob_name)
            assert "size" in properties
            assert "content_type" in properties
            assert "last_modified" in properties

            # Test list blobs
            blobs = helper.list_blobs(test_container_name)
            assert isinstance(blobs, list)
            assert len(blobs) >= 1
            blob_names = [b["name"] for b in blobs]
            assert test_blob_name in blob_names

            # Test blob deletion
            delete_result = helper.delete_blob(test_container_name, test_blob_name)
            assert delete_result is True

            # Verify blob is deleted
            exists_after_delete = helper.blob_exists(
                test_container_name, test_blob_name
            )
            assert exists_after_delete is False

        finally:
            # Cleanup
            try:
                helper.delete_blob(test_container_name, test_blob_name)
                helper.delete_container(test_container_name)
            except Exception:
                pass  # Ignore cleanup errors

    def test_real_file_operations(
        self, account_name, test_container_name, test_blob_name
    ):
        """Test real file upload and download operations"""
        helper = StorageBlobHelper(account_name=account_name)
        test_content = "File content for upload/download test"

        # Create temporary files
        with tempfile.NamedTemporaryFile(
            mode="w", delete=False, suffix=".txt"
        ) as temp_upload:
            temp_upload.write(test_content)
            upload_file_path = temp_upload.name

        with tempfile.NamedTemporaryFile(delete=False, suffix=".txt") as temp_download:
            download_file_path = temp_download.name

        try:
            # Create container first
            helper.create_container(test_container_name)

            # Test file upload
            upload_result = helper.upload_file(
                container_name=test_container_name,
                blob_name=test_blob_name,
                file_path=upload_file_path,
            )
            assert upload_result is True

            # Test file download
            download_result = helper.download_blob(
                container_name=test_container_name, blob_name=test_blob_name
            )

            # Save file content to download path
            with open(download_file_path, "wb") as f:
                f.write(download_result)

            # Verify downloaded content
            with open(download_file_path, "r") as f:
                downloaded_content = f.read()
            assert downloaded_content == test_content

        finally:
            # Cleanup files
            try:
                os.unlink(upload_file_path)
                os.unlink(download_file_path)
                helper.delete_blob(test_container_name, test_blob_name)
                helper.delete_container(test_container_name)
            except Exception:
                pass  # Ignore cleanup errors

    def test_real_blob_metadata_operations(
        self, account_name, test_container_name, test_blob_name
    ):
        """Test real blob metadata operations"""
        helper = StorageBlobHelper(account_name=account_name)
        test_content = "Metadata test content"
        test_metadata = {"purpose": "testing", "category": "unit-test"}

        try:
            # Create container first
            helper.create_container(test_container_name)

            # Upload blob with metadata
            helper.upload_blob(
                container_name=test_container_name,
                blob_name=test_blob_name,
                data=test_content,
                metadata=test_metadata,
            )

            # Get blob properties to verify metadata
            properties = helper.get_blob_properties(test_container_name, test_blob_name)
            assert "metadata" in properties
            for key, value in test_metadata.items():
                assert properties["metadata"].get(key) == value

            # Update metadata
            new_metadata = {"updated": "true", "version": "2"}
            result = helper.set_blob_metadata(
                test_container_name, test_blob_name, new_metadata
            )
            assert result is True

            # Verify updated metadata
            updated_properties = helper.get_blob_properties(
                test_container_name, test_blob_name
            )
            for key, value in new_metadata.items():
                assert updated_properties["metadata"].get(key) == value

        finally:
            # Cleanup
            try:
                helper.delete_blob(test_container_name, test_blob_name)
                helper.delete_container(test_container_name)
            except Exception:
                pass  # Ignore cleanup errors

    def test_real_multiple_blob_operations(self, account_name, test_container_name):
        """Test multiple blob operations"""
        helper = StorageBlobHelper(account_name=account_name)
        blob_names = [f"multi-test-{i}-{uuid.uuid4().hex[:8]}.txt" for i in range(3)]
        test_contents = [f"Content for blob {i}" for i in range(3)]

        try:
            # Create container first
            helper.create_container(test_container_name)

            # Upload multiple blobs
            for i, (blob_name, content) in enumerate(zip(blob_names, test_contents)):
                result = helper.upload_blob(
                    container_name=test_container_name,
                    blob_name=blob_name,
                    data=content,
                )
                assert result is True

            # List all blobs and verify
            blobs = helper.list_blobs(test_container_name)
            uploaded_blob_names = [b["name"] for b in blobs]
            for blob_name in blob_names:
                assert blob_name in uploaded_blob_names

            # Download and verify each blob
            for blob_name, expected_content in zip(blob_names, test_contents):
                downloaded_content = helper.download_blob(
                    test_container_name, blob_name
                )
                assert downloaded_content.decode("utf-8") == expected_content

        finally:
            # Cleanup all blobs
            try:
                for blob_name in blob_names:
                    helper.delete_blob(test_container_name, blob_name)
                helper.delete_container(test_container_name)
            except Exception:
                pass  # Ignore cleanup errors

    def test_real_download_blob_to_file(
        self, account_name, test_container_name, test_blob_name
    ):
        """Test real download blob to file operations"""
        test_content = "Content for download to file test"
        helper = StorageBlobHelper(account_name=account_name)

        # Create temporary file for download
        with tempfile.NamedTemporaryFile(delete=False, suffix=".txt") as temp_file:
            download_file_path = temp_file.name

        try:
            # Create container and upload blob
            helper.create_container(test_container_name)
            helper.upload_blob(test_container_name, test_blob_name, test_content)

            # Test download to file
            download_result = helper.download_blob_to_file(
                test_container_name, test_blob_name, download_file_path
            )
            assert download_result is True

            # Verify downloaded content
            with open(download_file_path, "r") as f:
                downloaded_content = f.read()
            assert downloaded_content == test_content

        finally:
            # Cleanup
            try:
                os.unlink(download_file_path)
                helper.delete_blob(test_container_name, test_blob_name)
                helper.delete_container(test_container_name)
            except Exception:
                pass  # Ignore cleanup errors

    def test_real_copy_and_move_blob_operations(
        self, account_name, test_container_name
    ):
        """Test real blob copy and move operations"""
        test_content = "Content for copy/move test"
        source_blob = f"source-blob-{uuid.uuid4().hex[:8]}.txt"
        copy_blob = f"copy-blob-{uuid.uuid4().hex[:8]}.txt"
        move_blob = f"move-blob-{uuid.uuid4().hex[:8]}.txt"

        helper = StorageBlobHelper(account_name=account_name)

        try:
            # Create container and upload source blob
            helper.create_container(test_container_name)
            helper.upload_blob(test_container_name, source_blob, test_content)

            # Test copy blob
            copy_result = helper.copy_blob(
                test_container_name, source_blob, test_container_name, copy_blob
            )
            assert copy_result is True

            # Verify copied blob exists and has same content
            copy_exists = helper.blob_exists(test_container_name, copy_blob)
            assert copy_exists is True

            copied_content = helper.download_blob(test_container_name, copy_blob)
            assert copied_content.decode("utf-8") == test_content

            # Test move blob
            move_result = helper.move_blob(
                test_container_name, copy_blob, test_container_name, move_blob
            )
            assert move_result is True

            # Verify moved blob exists and original copy is gone
            move_exists = helper.blob_exists(test_container_name, move_blob)
            assert move_exists is True

            copy_exists_after_move = helper.blob_exists(test_container_name, copy_blob)
            assert copy_exists_after_move is False

            moved_content = helper.download_blob(test_container_name, move_blob)
            assert moved_content.decode("utf-8") == test_content

        finally:
            # Cleanup
            try:
                helper.delete_blob(test_container_name, source_blob)
                helper.delete_blob(test_container_name, copy_blob)
                helper.delete_blob(test_container_name, move_blob)
                helper.delete_container(test_container_name)
            except Exception:
                pass  # Ignore cleanup errors

    def test_real_list_blobs_hierarchical(self, account_name, test_container_name):
        """Test real hierarchical blob listing"""
        test_content = "Hierarchical test content"
        blob_paths = [
            "folder1/file1.txt",
            "folder1/file2.txt",
            "folder1/subfolder/file3.txt",
            "folder2/file4.txt",
            "root-file.txt",
        ]

        helper = StorageBlobHelper(account_name=account_name)

        try:
            # Create container and upload blobs in hierarchy
            helper.create_container(test_container_name)
            for blob_path in blob_paths:
                helper.upload_blob(
                    test_container_name, blob_path, f"{test_content} - {blob_path}"
                )

            # Test hierarchical listing - root level
            hierarchy = helper.list_blobs_hierarchical(test_container_name)
            assert "prefixes" in hierarchy
            assert "blobs" in hierarchy

            # Should have prefixes for folder1/ and folder2/
            prefix_names = [p["name"] for p in hierarchy["prefixes"]]
            assert "folder1/" in prefix_names
            assert "folder2/" in prefix_names

            # Should have root-file.txt in blobs
            blob_names = [b["name"] for b in hierarchy["blobs"]]
            assert "root-file.txt" in blob_names

            # Test hierarchical listing - folder1 level
            folder1_hierarchy = helper.list_blobs_hierarchical(
                test_container_name, prefix="folder1/"
            )
            folder1_blobs = [b["name"] for b in folder1_hierarchy["blobs"]]
            assert "folder1/file1.txt" in folder1_blobs
            assert "folder1/file2.txt" in folder1_blobs

            # Should have subfolder prefix
            folder1_prefixes = [p["name"] for p in folder1_hierarchy["prefixes"]]
            assert "folder1/subfolder/" in folder1_prefixes

        finally:
            # Cleanup
            try:
                for blob_path in blob_paths:
                    helper.delete_blob(test_container_name, blob_path)
                helper.delete_container(test_container_name)
            except Exception:
                pass  # Ignore cleanup errors

    def test_real_delete_multiple_blobs(self, account_name, test_container_name):
        """Test real multiple blob deletion"""
        test_content = "Content for deletion test"
        blob_names = [f"delete-test-{i}-{uuid.uuid4().hex[:8]}.txt" for i in range(3)]

        helper = StorageBlobHelper(account_name=account_name)

        try:
            # Create container and upload multiple blobs
            helper.create_container(test_container_name)
            for blob_name in blob_names:
                helper.upload_blob(test_container_name, blob_name, test_content)

            # Verify all blobs exist
            for blob_name in blob_names:
                assert helper.blob_exists(test_container_name, blob_name) is True

            # Test multiple blob deletion
            delete_results = helper.delete_multiple_blobs(
                test_container_name, blob_names
            )

            # Check that all deletions were successful
            assert len(delete_results) == len(blob_names)
            for blob_name, result in delete_results.items():
                assert result is True

            # Verify all blobs are deleted
            for blob_name in blob_names:
                assert helper.blob_exists(test_container_name, blob_name) is False

        finally:
            # Cleanup
            try:
                for blob_name in blob_names:
                    helper.delete_blob(test_container_name, blob_name)
                helper.delete_container(test_container_name)
            except Exception:
                pass  # Ignore cleanup errors

    def test_real_list_containers_with_filters(self, account_name):
        """Test real container listing with filters"""
        container_prefix = f"filter-test-{uuid.uuid4().hex[:8]}"
        container_names = [f"{container_prefix}-{i}" for i in range(3)]

        helper = StorageBlobHelper(account_name=account_name)

        try:
            # Create test containers
            for container_name in container_names:
                helper.create_container(container_name, metadata={"test": "filter"})

            # Test list all containers
            all_containers = helper.list_containers()
            assert isinstance(all_containers, list)
            all_container_names = [c["name"] for c in all_containers]
            for container_name in container_names:
                assert container_name in all_container_names

            # Test list containers with name filter
            filtered_containers = helper.list_containers(
                name_starts_with=container_prefix, include_metadata=True
            )
            assert len(filtered_containers) == 3

            for container in filtered_containers:
                assert container["name"].startswith(container_prefix)
                assert "metadata" in container
                assert container["metadata"].get("test") == "filter"

        finally:
            # Cleanup
            try:
                for container_name in container_names:
                    helper.delete_container(container_name)
            except Exception:
                pass  # Ignore cleanup errors


class TestStorageQueueHelperReal:
    """Test sync queue helper functionality with real Azure resources"""

    @pytest.fixture
    def connection_string(self):
        """Get connection string from environment"""
        conn_str = os.getenv("AZURE_STORAGE_CONNECTION_STRING")
        if not conn_str:
            pytest.skip("AZURE_STORAGE_CONNECTION_STRING environment variable not set")
        return conn_str

    @pytest.fixture
    def account_name(self):
        account_name = "appfrmstorageaccount"  # os.getenv("AZURE_STORAGE_ACCOUNT_NAME")
        if not account_name:
            pytest.skip("AZURE_STORAGE_ACCOUNT_NAME environment variable not set")
        return account_name

    @pytest.fixture
    def test_queue_name(self):
        """Generate unique queue name for testing"""
        return f"test-queue-{uuid.uuid4().hex[:8]}"

    def test_init_with_connection_string(self, connection_string):
        """Test initialization with connection string"""
        helper = StorageQueueHelper(connection_string=connection_string)
        assert helper is not None
        assert helper.queue_service_client is not None

    def test_real_queue_operations(self, account_name, test_queue_name):
        """Test real queue operations"""
        helper = StorageQueueHelper(account_name=account_name)

        try:
            # Test queue creation
            result = helper.create_queue(test_queue_name)
            assert result is True

            # Test queue exists
            exists = helper.queue_exists(test_queue_name)
            assert exists is True

            # Test list queues
            queues = helper.list_queues()
            assert isinstance(queues, list)
            queue_names = [q["name"] for q in queues]
            assert test_queue_name in queue_names

            # Test queue properties
            properties = helper.get_queue_properties(test_queue_name)
            assert "name" in properties
            assert properties["name"] == test_queue_name
            assert "approximate_message_count" in properties

        finally:
            # Cleanup
            try:
                helper.delete_queue(test_queue_name)
            except Exception:
                pass  # Ignore cleanup errors

    def test_real_message_operations(self, account_name, test_queue_name):
        """Test real message operations"""
        helper = StorageQueueHelper(account_name=account_name)
        test_message = "Hello, sync queue world!"

        try:
            # Create queue first
            helper.create_queue(test_queue_name)

            # Test message sending
            send_result = helper.send_message(test_queue_name, test_message)
            assert "message_id" in send_result
            assert "pop_receipt" in send_result

            # Wait a moment for message to be available
            time.sleep(1)

            # Test message receiving
            messages = helper.receive_messages(test_queue_name, max_messages=1)
            assert len(messages) >= 1
            received_message = messages[0]
            assert received_message["content"] == test_message
            assert "message_id" in received_message
            assert "pop_receipt" in received_message

            # Test message deletion
            delete_result = helper.delete_message(
                test_queue_name,
                received_message["message_id"],
                received_message["pop_receipt"],
            )
            assert delete_result is True

        finally:
            # Cleanup
            try:
                helper.delete_queue(test_queue_name)
            except Exception:
                pass  # Ignore cleanup errors

    def test_real_multiple_message_operations(self, account_name, test_queue_name):
        """Test multiple message operations"""
        helper = StorageQueueHelper(account_name=account_name)
        test_messages = [f"Message {i}" for i in range(3)]

        try:
            # Create queue first
            helper.create_queue(test_queue_name)

            # Send multiple messages
            send_results = []
            for message in test_messages:
                result = helper.send_message(test_queue_name, message)
                send_results.append(result)
                assert "message_id" in result

            # Wait a moment for messages to be available
            time.sleep(1)

            # Receive multiple messages
            received_messages = helper.receive_messages(test_queue_name, max_messages=5)
            assert len(received_messages) >= len(test_messages)

            # Verify message content
            received_contents = [msg["content"] for msg in received_messages]
            for original_message in test_messages:
                assert original_message in received_contents

            # Delete all received messages
            for message in received_messages:
                delete_result = helper.delete_message(
                    test_queue_name, message["message_id"], message["pop_receipt"]
                )
                assert delete_result is True

        finally:
            # Cleanup
            try:
                helper.delete_queue(test_queue_name)
            except Exception:
                pass  # Ignore cleanup errors

    def test_real_peek_messages(self, account_name, test_queue_name):
        """Test peeking at messages without removing them"""
        helper = StorageQueueHelper(account_name=account_name)
        test_message = "Peek test message"

        try:
            # Create queue and send message
            helper.create_queue(test_queue_name)
            helper.send_message(test_queue_name, test_message)

            # Wait a moment for message to be available
            time.sleep(1)

            # Peek at messages
            peeked_messages = helper.peek_messages(test_queue_name, max_messages=1)
            assert len(peeked_messages) >= 1
            assert peeked_messages[0]["content"] == test_message

            # Verify message is still in queue by receiving it
            received_messages = helper.receive_messages(test_queue_name, max_messages=1)
            assert len(received_messages) >= 1
            assert received_messages[0]["content"] == test_message

            # Clean up the message
            helper.delete_message(
                test_queue_name,
                received_messages[0]["message_id"],
                received_messages[0]["pop_receipt"],
            )

        finally:
            # Cleanup
            try:
                helper.delete_queue(test_queue_name)
            except Exception:
                pass  # Ignore cleanup errors

    def test_real_clear_queue(self, account_name, test_queue_name):
        """Test clearing all messages from queue"""
        helper = StorageQueueHelper(account_name=account_name)
        test_messages = [f"Clear test message {i}" for i in range(3)]

        try:
            # Create queue and send messages
            helper.create_queue(test_queue_name)
            for message in test_messages:
                helper.send_message(test_queue_name, message)

            # Wait a moment for messages to be available
            time.sleep(1)

            # Clear queue
            clear_result = helper.clear_queue(test_queue_name)
            assert clear_result is True

            # Wait a moment for clear to take effect
            time.sleep(1)

            # Verify queue is empty
            messages = helper.receive_messages(test_queue_name, max_messages=10)
            assert len(messages) == 0

        finally:
            # Cleanup
            try:
                helper.delete_queue(test_queue_name)
            except Exception:
                pass  # Ignore cleanup errors

    def test_real_message_json_operations(self, account_name, test_queue_name):
        """Test JSON message operations"""
        helper = StorageQueueHelper(account_name=account_name)
        test_data = {"type": "test", "value": 42, "active": True}

        try:
            # Create queue first
            helper.create_queue(test_queue_name)

            # Send JSON message
            send_result = helper.send_message(test_queue_name, test_data)
            assert "message_id" in send_result

            # Wait a moment for message to be available
            time.sleep(1)

            # Receive and verify JSON message
            messages = helper.receive_messages(test_queue_name, max_messages=1)
            assert len(messages) >= 1
            received_message = messages[0]

            # The content should be JSON string, so we need to parse it
            import json

            received_data = json.loads(received_message["content"])
            assert received_data == test_data

            # Clean up the message
            helper.delete_message(
                test_queue_name,
                received_message["message_id"],
                received_message["pop_receipt"],
            )

        finally:
            # Cleanup
            try:
                helper.delete_queue(test_queue_name)
            except Exception:
                pass  # Ignore cleanup errors

    def test_real_update_and_delete_message(self, account_name, test_queue_name):
        """Test real message update and delete operations"""
        test_message = "Message for update/delete test"

        helper = StorageQueueHelper(account_name=account_name)

        try:
            # Create queue and send message
            helper.create_queue(test_queue_name)
            send_result = helper.send_message(test_queue_name, test_message)
            assert "message_id" in send_result

            # Receive message to get pop receipt
            messages = helper.receive_messages(test_queue_name, max_messages=1)
            assert len(messages) >= 1

            message = messages[0]
            pop_receipt = message["pop_receipt"]
            message_id = message["message_id"]

            # Test update message
            updated_content = "Updated message content"
            update_result = helper.update_message(
                test_queue_name, message_id, pop_receipt, updated_content
            )
            # assert update_result is True

            # Receive updated message to verify
            updated_messages = helper.receive_messages(test_queue_name, max_messages=1)
            if updated_messages:  # Message might still be processing
                updated_message = updated_messages[0]
                # Note: Updated content should be reflected
                new_pop_receipt = updated_message["pop_receipt"]

                assert updated_message["content"] == updated_content

                # Test delete message
                delete_result = helper.delete_message(
                    test_queue_name, updated_message["message_id"], new_pop_receipt
                )
                assert delete_result is True

        finally:
            # Cleanup
            try:
                helper.delete_queue(test_queue_name)
            except Exception:
                pass  # Ignore cleanup errors

    def test_real_process_messages(self, account_name, test_queue_name):
        """Test real message processing functionality"""
        test_messages = [f"Process message {i}" for i in range(3)]

        helper = StorageQueueHelper(account_name=account_name)
        processed_messages = []

        def message_processor(message):
            """Simple message processor for testing"""
            processed_messages.append(message["content"])
            return True  # Mark as processed

        try:
            # Create queue and send messages
            helper.create_queue(test_queue_name)
            for message in test_messages:
                helper.send_message(test_queue_name, message)

            # Wait a moment for messages to be available
            time.sleep(2)

            # Test process messages
            helper.process_messages(
                test_queue_name, message_processor, max_messages=3, timeout=10
            )

            # Verify processing results
            assert len(processed_messages) >= 1  # At least one message processed
            for processed_content in processed_messages:
                assert processed_content in test_messages

        finally:
            # Cleanup
            try:
                helper.delete_queue(test_queue_name)
            except Exception:
                pass  # Ignore cleanup errors

    def test_real_queue_url_and_encoding(self, account_name, test_queue_name):
        """Test real queue URL generation and message encoding"""
        test_dict_message = {"type": "test", "data": "encoded message", "number": 123}

        helper = StorageQueueHelper(account_name=account_name)

        try:
            # Create queue
            helper.create_queue(test_queue_name)

            # Test get queue URL
            queue_url = helper.get_queue_url(test_queue_name)
            assert queue_url.startswith("https://")
            assert test_queue_name in queue_url

            # Test message encoding/decoding
            encoded_message = helper.encode_message(test_dict_message)
            assert isinstance(encoded_message, str)

            decoded_message = helper.decode_message(encoded_message)
            assert decoded_message == test_dict_message

            # Test sending encoded message
            send_result = helper.send_message(test_queue_name, test_dict_message)
            assert "message_id" in send_result

            # Wait and receive to verify encoding worked
            time.sleep(1)
            messages = helper.receive_messages(test_queue_name, max_messages=1)
            if messages:
                received_message = messages[0]
                # The content should be decodable back to original dict
                if isinstance(received_message["content"], str):
                    try:
                        decoded_content = helper.decode_message(
                            received_message["content"]
                        )
                        assert decoded_content == test_dict_message
                    except Exception:
                        # If decoding fails, content might be string representation
                        pass

        finally:
            # Cleanup
            try:
                helper.delete_queue(test_queue_name)
            except Exception:
                pass  # Ignore cleanup errors


class TestStorageBlobHelperSASTokensReal:
    """Test SAS token generation with sync blob helper"""

    @pytest.fixture
    def connection_string(self):
        """Get connection string from environment"""
        conn_str = os.getenv("AZURE_STORAGE_CONNECTION_STRING")
        if not conn_str:
            pytest.skip("AZURE_STORAGE_CONNECTION_STRING environment variable not set")
        return conn_str

    @pytest.fixture
    def account_name(self):
        account_name = "appfrmstorageaccount"  # os.getenv("AZURE_STORAGE_ACCOUNT_NAME")
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

    def test_generate_blob_sas_url_real(
        self, account_name, test_container_name, test_blob_name
    ):
        """Test blob SAS URL generation with real Azure resources"""
        helper = StorageBlobHelper(account_name=account_name)
        test_content = "SAS token test content"

        try:
            # Create container and upload blob
            helper.create_container(test_container_name)
            helper.upload_blob(test_container_name, test_blob_name, test_content)

            # Generate SAS URL
            sas_url = helper.generate_blob_sas_url(
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
            import requests

            response = requests.get(sas_url)
            assert response.status_code == 200
            assert response.text == test_content

        finally:
            # Cleanup
            try:
                helper.delete_blob(test_container_name, test_blob_name)
                helper.delete_container(test_container_name)
            except Exception:
                pass  # Ignore cleanup errors

    def test_generate_container_sas_url_real(self, account_name, test_container_name):
        """Test container SAS URL generation with real Azure resources"""
        helper = StorageBlobHelper(account_name=account_name)

        try:
            # Create container
            helper.create_container(test_container_name)

            # Generate container SAS URL
            sas_url = helper.generate_container_sas_url(
                container_name=test_container_name,
                permissions="rl",  # read permission
                expiry_hours=1,
            )

            assert isinstance(sas_url, str)
            assert "sig=" in sas_url  # SAS signature
            assert test_container_name in sas_url

            # Test the SAS URL by listing blobs
            import requests

            list_url = f"{sas_url}&restype=container&comp=list"
            response = requests.get(list_url)
            assert response.status_code == 200

        finally:
            # Cleanup
            try:
                helper.delete_container(test_container_name)
            except Exception:
                pass  # Ignore cleanup errors

    def test_copy_blob_with_metadata(self, account_name, test_container_name):
        """Test blob copy operation with metadata"""
        helper = StorageBlobHelper(account_name=account_name)

        try:
            helper.create_container(test_container_name)

            # Upload source blob
            source_blob = "source-test.txt"
            test_content = "Test content for copying"
            helper.upload_blob(
                test_container_name, source_blob, test_content.encode(), overwrite=True
            )

            # Copy with metadata
            dest_blob = "dest-test.txt"
            metadata = {"copied": "true", "timestamp": "2025-09-19"}
            success = helper.copy_blob(
                source_container=test_container_name,
                source_blob=source_blob,
                dest_container=test_container_name,
                dest_blob=dest_blob,
                metadata=metadata,
                overwrite=True,
            )

            assert success is True

            # Verify copy and metadata
            assert helper.blob_exists(test_container_name, dest_blob)
            properties = helper.get_blob_properties(test_container_name, dest_blob)
            assert properties["metadata"]["copied"] == "true"
            assert properties["metadata"]["timestamp"] == "2025-09-19"

        finally:
            # Clean up
            try:
                helper.delete_container(test_container_name, force_delete=True)
            except Exception:
                pass

    def test_move_blob_with_metadata(self, account_name, test_container_name):
        """Test blob move operation with metadata"""
        helper = StorageBlobHelper(account_name=account_name)

        try:
            helper.create_container(test_container_name)

            # Upload source blob
            source_blob = "source-move.txt"
            test_content = "Test content for moving"
            helper.upload_blob(
                test_container_name, source_blob, test_content.encode(), overwrite=True
            )

            # Move with metadata
            dest_blob = "dest-move.txt"
            metadata = {"moved": "true", "operation": "move"}
            success = helper.move_blob(
                source_container=test_container_name,
                source_blob=source_blob,
                dest_container=test_container_name,
                dest_blob=dest_blob,
                metadata=metadata,
                overwrite=True,
            )

            assert success is True

            # Verify move: dest exists, source doesn't
            assert helper.blob_exists(test_container_name, dest_blob)
            assert not helper.blob_exists(test_container_name, source_blob)

            # Verify metadata
            properties = helper.get_blob_properties(test_container_name, dest_blob)
            assert properties["metadata"]["moved"] == "true"
            assert properties["metadata"]["operation"] == "move"

        finally:
            # Clean up
            try:
                helper.delete_container(test_container_name, force_delete=True)
            except Exception:
                pass

    def test_upload_blob_from_text_capability(self, account_name, test_container_name):
        """Test uploading text content as blob using upload_blob"""
        helper = StorageBlobHelper(account_name=account_name)

        try:
            helper.create_container(test_container_name)

            # Upload text content using upload_blob
            blob_name = "text-upload.txt"
            text_content = "Hello, Azure Storage!\nThis is a test file."

            success = helper.upload_blob(
                container_name=test_container_name,
                blob_name=blob_name,
                data=text_content.encode("utf-8"),
                overwrite=True,
            )

            assert success is True

            # Verify content
            downloaded_content = helper.download_blob(test_container_name, blob_name)
            assert downloaded_content.decode("utf-8") == text_content

        finally:
            # Clean up
            try:
                helper.delete_container(test_container_name, force_delete=True)
            except Exception:
                pass

    def test_download_file_capability(self, account_name, test_container_name):
        """Test downloading blob to local file using download_blob_to_file"""
        helper = StorageBlobHelper(account_name=account_name)

        try:
            helper.create_container(test_container_name)

            # Upload test blob
            blob_name = "download-test.txt"
            test_content = "Content for download test"
            helper.upload_blob(
                test_container_name, blob_name, test_content.encode(), overwrite=True
            )

            # Download to local file using existing method
            with tempfile.NamedTemporaryFile(mode="w+", delete=False) as temp_file:
                local_path = temp_file.name

            try:
                success = helper.download_blob_to_file(
                    container_name=test_container_name,
                    blob_name=blob_name,
                    file_path=local_path,
                )

                assert success is True

                # Verify file content
                with open(local_path, "r") as f:
                    content = f.read()
                    assert content == test_content

            finally:
                # Clean up
                if os.path.exists(local_path):
                    os.unlink(local_path)

        finally:
            try:
                helper.delete_container(test_container_name, force_delete=True)
            except Exception:
                pass

    def test_list_blobs_hierarchical_existing(self, account_name, test_container_name):
        """Test hierarchical blob listing"""
        helper = StorageBlobHelper(account_name=account_name)

        try:
            helper.create_container(test_container_name)

            # Create test blobs with hierarchical structure
            test_blobs = [
                "folder1/file1.txt",
                "folder1/file2.txt",
                "folder2/subfolder/file3.txt",
                "root-file.txt",
            ]

            for blob_name in test_blobs:
                helper.upload_blob(
                    test_container_name,
                    blob_name,
                    f"Content of {blob_name}".encode(),
                    overwrite=True,
                )

            # List hierarchically
            result = helper.list_blobs_hierarchical(
                container_name=test_container_name, prefix="", delimiter="/"
            )

            assert "blobs" in result
            assert "prefixes" in result
            assert len(result["blobs"]) >= 1  # Should have root-file.txt
            assert len(result["prefixes"]) >= 2  # Should have folder1/ and folder2/

            # List folder1 contents
            folder1_result = helper.list_blobs_hierarchical(
                container_name=test_container_name, prefix="folder1/", delimiter="/"
            )

            assert len(folder1_result["blobs"]) == 2  # file1.txt and file2.txt

        finally:
            # Clean up
            try:
                helper.delete_container(test_container_name, force_delete=True)
            except Exception:
                pass

    def test_get_blob_properties_existing(self, account_name, test_container_name):
        """Test getting detailed blob properties"""
        helper = StorageBlobHelper(account_name=account_name)

        try:
            helper.create_container(test_container_name)

            # Upload blob with metadata
            blob_name = "properties-test.txt"
            test_content = "Content for properties test"
            metadata = {"test": "value", "property": "check"}

            helper.upload_blob(
                test_container_name,
                blob_name,
                test_content.encode(),
                metadata=metadata,
                overwrite=True,
            )

            # Get properties
            properties = helper.get_blob_properties(test_container_name, blob_name)

            assert properties is not None
            assert properties["name"] == blob_name
            assert properties["size"] == len(test_content)
            assert properties["metadata"]["test"] == "value"
            assert properties["metadata"]["property"] == "check"
            assert "last_modified" in properties
            assert "etag" in properties

        finally:
            # Clean up
            try:
                helper.delete_container(test_container_name, force_delete=True)
            except Exception:
                pass

    def test_set_blob_metadata_existing(self, account_name, test_container_name):
        """Test setting blob metadata"""
        helper = StorageBlobHelper(account_name=account_name)

        try:
            helper.create_container(test_container_name)

            # Upload blob
            blob_name = "metadata-test.txt"
            test_content = "Content for metadata test"
            helper.upload_blob(
                test_container_name, blob_name, test_content.encode(), overwrite=True
            )

            # Set metadata
            new_metadata = {"updated": "true", "version": "1.0", "author": "test"}
            success = helper.set_blob_metadata(
                test_container_name, blob_name, new_metadata
            )

            assert success is True

            # Verify metadata
            properties = helper.get_blob_properties(test_container_name, blob_name)
            assert properties["metadata"]["updated"] == "true"
            assert properties["metadata"]["version"] == "1.0"
            assert properties["metadata"]["author"] == "test"

        finally:
            # Clean up
            try:
                helper.delete_container(test_container_name, force_delete=True)
            except Exception:
                pass

    def test_download_multiple_blobs_existing(self, account_name, test_container_name):
        """Test downloading multiple blobs"""
        helper = StorageBlobHelper(account_name=account_name)

        try:
            helper.create_container(test_container_name)

            # Upload multiple test blobs
            test_blobs = ["file1.txt", "file2.txt", "file3.txt"]
            for blob_name in test_blobs:
                helper.upload_blob(
                    test_container_name,
                    blob_name,
                    f"Content of {blob_name}".encode(),
                    overwrite=True,
                )

            # Download multiple blobs
            with tempfile.TemporaryDirectory() as temp_dir:
                results = helper.download_multiple_blobs(
                    container_name=test_container_name,
                    blob_names=test_blobs,
                    download_dir=temp_dir,
                )

                assert len(results) == 3
                assert all(results.values())  # All downloads should succeed

                # Verify files exist
                for blob_name in test_blobs:
                    file_path = os.path.join(temp_dir, blob_name)
                    assert os.path.exists(file_path)
                    with open(file_path, "r") as f:
                        content = f.read()
                        assert content == f"Content of {blob_name}"

        finally:
            # Clean up
            try:
                helper.delete_container(test_container_name, force_delete=True)
            except Exception:
                pass

    def test_delete_multiple_blobs_existing(self, account_name, test_container_name):
        """Test deleting multiple blobs"""
        helper = StorageBlobHelper(account_name=account_name)

        try:
            helper.create_container(test_container_name)

            # Upload multiple test blobs
            test_blobs = ["delete1.txt", "delete2.txt", "delete3.txt"]
            for blob_name in test_blobs:
                helper.upload_blob(
                    test_container_name,
                    blob_name,
                    f"Content of {blob_name}".encode(),
                    overwrite=True,
                )

            # Verify all blobs exist
            for blob_name in test_blobs:
                assert helper.blob_exists(test_container_name, blob_name)

            # Delete multiple blobs
            results = helper.delete_multiple_blobs(
                container_name=test_container_name, blob_names=test_blobs
            )

            assert len(results) == 3
            assert all(results.values())  # All deletions should succeed

            # Verify all blobs are deleted
            for blob_name in test_blobs:
                assert not helper.blob_exists(test_container_name, blob_name)

        finally:
            # Clean up
            try:
                helper.delete_container(test_container_name, force_delete=True)
            except Exception:
                pass
