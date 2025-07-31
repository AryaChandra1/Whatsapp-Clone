#!/usr/bin/env python3
"""
WhatsApp AI Clone Backend Testing Suite
Tests all backend API endpoints and AI personality system
"""

import requests
import json
import time
from datetime import datetime
from typing import Dict, List, Any
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv('/app/frontend/.env')

# Get backend URL from environment
BACKEND_URL = os.getenv('EXPO_PUBLIC_BACKEND_URL', 'http://localhost:8001')
API_BASE_URL = f"{BACKEND_URL}/api"

print(f"Testing backend at: {API_BASE_URL}")

class WhatsAppAITester:
    def __init__(self):
        self.session = requests.Session()
        self.test_results = {
            'total_tests': 0,
            'passed_tests': 0,
            'failed_tests': 0,
            'errors': []
        }
        self.chat_ids = {}  # Store chat IDs for different personalities
        
    def log_test(self, test_name: str, passed: bool, message: str = ""):
        """Log test results"""
        self.test_results['total_tests'] += 1
        if passed:
            self.test_results['passed_tests'] += 1
            print(f"✅ {test_name}: PASSED {message}")
        else:
            self.test_results['failed_tests'] += 1
            self.test_results['errors'].append(f"{test_name}: {message}")
            print(f"❌ {test_name}: FAILED {message}")
    
    def test_api_health(self):
        """Test if API is accessible"""
        try:
            response = self.session.get(f"{API_BASE_URL}/")
            if response.status_code == 200:
                data = response.json()
                if "WhatsApp AI Clone API" in data.get('message', ''):
                    self.log_test("API Health Check", True, "API is accessible")
                    return True
                else:
                    self.log_test("API Health Check", False, f"Unexpected response: {data}")
                    return False
            else:
                self.log_test("API Health Check", False, f"Status code: {response.status_code}")
                return False
        except Exception as e:
            self.log_test("API Health Check", False, f"Connection error: {str(e)}")
            return False
    
    def test_get_chats(self):
        """Test GET /api/chats endpoint"""
        try:
            response = self.session.get(f"{API_BASE_URL}/chats")
            if response.status_code == 200:
                chats = response.json()
                
                # Check if we have 10 AI personalities
                if len(chats) == 10:
                    self.log_test("Get Chats - Count", True, f"Found {len(chats)} AI personalities")
                else:
                    self.log_test("Get Chats - Count", False, f"Expected 10 personalities, got {len(chats)}")
                
                # Store chat IDs for later tests
                expected_personalities = ['alex_sarcastic', 'maya_mentor', 'zoe_tech', 'ryan_flirty']
                found_personalities = []
                
                for chat in chats:
                    personality = chat.get('ai_personality')
                    self.chat_ids[personality] = chat.get('id')
                    found_personalities.append(personality)
                    
                    # Validate chat structure
                    required_fields = ['id', 'ai_personality', 'name', 'avatar', 'description', 'last_seen']
                    missing_fields = [field for field in required_fields if field not in chat]
                    
                    if missing_fields:
                        self.log_test(f"Chat Structure - {personality}", False, f"Missing fields: {missing_fields}")
                    else:
                        self.log_test(f"Chat Structure - {personality}", True, "All required fields present")
                
                # Check if target personalities are present
                for personality in expected_personalities:
                    if personality in found_personalities:
                        self.log_test(f"Personality Present - {personality}", True)
                    else:
                        self.log_test(f"Personality Present - {personality}", False, "Personality not found")
                
                return True
            else:
                self.log_test("Get Chats", False, f"Status code: {response.status_code}")
                return False
                
        except Exception as e:
            self.log_test("Get Chats", False, f"Error: {str(e)}")
            return False
    
    def test_send_message_to_personality(self, personality: str, test_message: str, expected_traits: List[str]):
        """Test sending a message to a specific AI personality"""
        if personality not in self.chat_ids:
            self.log_test(f"Send Message - {personality}", False, "Chat ID not found")
            return False
        
        chat_id = self.chat_ids[personality]
        
        try:
            # Send message
            message_data = {
                "chat_id": chat_id,
                "content": test_message
            }
            
            response = self.session.post(f"{API_BASE_URL}/chats/{chat_id}/messages", json=message_data)
            
            if response.status_code == 200:
                ai_response = response.json()
                
                # Validate response structure
                required_fields = ['id', 'chat_id', 'sender_type', 'sender_name', 'content', 'timestamp', 'message_status']
                missing_fields = [field for field in required_fields if field not in ai_response]
                
                if missing_fields:
                    self.log_test(f"Message Response Structure - {personality}", False, f"Missing fields: {missing_fields}")
                    return False
                
                # Check if response is from AI
                if ai_response.get('sender_type') != 'ai':
                    self.log_test(f"Message Sender Type - {personality}", False, f"Expected 'ai', got '{ai_response.get('sender_type')}'")
                    return False
                
                # Check AI response content
                ai_content = ai_response.get('content', '').lower()
                personality_match = any(trait.lower() in ai_content for trait in expected_traits)
                
                self.log_test(f"Send Message - {personality}", True, f"Response: {ai_response.get('content')[:100]}...")
                
                if personality_match:
                    self.log_test(f"Personality Traits - {personality}", True, f"Response shows expected traits")
                else:
                    self.log_test(f"Personality Traits - {personality}", False, f"Response doesn't show expected traits: {expected_traits}")
                
                return True
            else:
                self.log_test(f"Send Message - {personality}", False, f"Status code: {response.status_code}, Response: {response.text}")
                return False
                
        except Exception as e:
            self.log_test(f"Send Message - {personality}", False, f"Error: {str(e)}")
            return False
    
    def test_get_chat_messages(self, personality: str):
        """Test GET /api/chats/{chat_id}/messages endpoint"""
        if personality not in self.chat_ids:
            self.log_test(f"Get Messages - {personality}", False, "Chat ID not found")
            return False
        
        chat_id = self.chat_ids[personality]
        
        try:
            response = self.session.get(f"{API_BASE_URL}/chats/{chat_id}/messages")
            
            if response.status_code == 200:
                messages = response.json()
                
                if len(messages) >= 2:  # Should have user message and AI response
                    # Check message ordering (should be chronological)
                    timestamps = [msg.get('timestamp') for msg in messages]
                    is_ordered = all(timestamps[i] <= timestamps[i+1] for i in range(len(timestamps)-1))
                    
                    if is_ordered:
                        self.log_test(f"Message Ordering - {personality}", True, "Messages are in chronological order")
                    else:
                        self.log_test(f"Message Ordering - {personality}", False, "Messages are not properly ordered")
                    
                    # Check for both user and AI messages
                    sender_types = [msg.get('sender_type') for msg in messages]
                    has_user_msg = 'user' in sender_types
                    has_ai_msg = 'ai' in sender_types
                    
                    if has_user_msg and has_ai_msg:
                        self.log_test(f"Message Types - {personality}", True, "Both user and AI messages present")
                    else:
                        self.log_test(f"Message Types - {personality}", False, f"Missing message types. User: {has_user_msg}, AI: {has_ai_msg}")
                    
                    self.log_test(f"Get Messages - {personality}", True, f"Retrieved {len(messages)} messages")
                    return True
                else:
                    self.log_test(f"Get Messages - {personality}", False, f"Expected at least 2 messages, got {len(messages)}")
                    return False
            else:
                self.log_test(f"Get Messages - {personality}", False, f"Status code: {response.status_code}")
                return False
                
        except Exception as e:
            self.log_test(f"Get Messages - {personality}", False, f"Error: {str(e)}")
            return False
    
    def test_openai_integration(self):
        """Test OpenAI integration by sending a message that requires AI processing"""
        personality = 'alex_sarcastic'
        if personality not in self.chat_ids:
            self.log_test("OpenAI Integration", False, "Alex chat not available")
            return False
        
        chat_id = self.chat_ids[personality]
        
        try:
            # Send a message that should trigger a sarcastic response
            message_data = {
                "chat_id": chat_id,
                "content": "I think I'm the smartest person in the world!"
            }
            
            response = self.session.post(f"{API_BASE_URL}/chats/{chat_id}/messages", json=message_data)
            
            if response.status_code == 200:
                ai_response = response.json()
                ai_content = ai_response.get('content', '')
                
                # Check if response is not a fallback message
                if "having trouble responding" not in ai_content.lower():
                    self.log_test("OpenAI Integration", True, f"AI generated response: {ai_content[:100]}...")
                    return True
                else:
                    self.log_test("OpenAI Integration", False, "Received fallback response - OpenAI may not be working")
                    return False
            else:
                self.log_test("OpenAI Integration", False, f"Failed to send message: {response.status_code}")
                return False
                
        except Exception as e:
            self.log_test("OpenAI Integration", False, f"Error: {str(e)}")
            return False
    
    def test_message_persistence(self):
        """Test that messages are properly stored in MongoDB"""
        personality = 'maya_mentor'
        if personality not in self.chat_ids:
            self.log_test("Message Persistence", False, "Maya chat not available")
            return False
        
        chat_id = self.chat_ids[personality]
        
        try:
            # Get initial message count
            response1 = self.session.get(f"{API_BASE_URL}/chats/{chat_id}/messages")
            if response1.status_code != 200:
                self.log_test("Message Persistence", False, "Failed to get initial messages")
                return False
            
            initial_count = len(response1.json())
            
            # Send a new message
            message_data = {
                "chat_id": chat_id,
                "content": "Can you give me some life advice?"
            }
            
            response2 = self.session.post(f"{API_BASE_URL}/chats/{chat_id}/messages", json=message_data)
            if response2.status_code != 200:
                self.log_test("Message Persistence", False, "Failed to send message")
                return False
            
            # Wait a moment for processing
            time.sleep(1)
            
            # Get updated message count
            response3 = self.session.get(f"{API_BASE_URL}/chats/{chat_id}/messages")
            if response3.status_code != 200:
                self.log_test("Message Persistence", False, "Failed to get updated messages")
                return False
            
            final_count = len(response3.json())
            
            # Should have 2 more messages (user + AI response)
            if final_count >= initial_count + 2:
                self.log_test("Message Persistence", True, f"Messages persisted correctly. Count: {initial_count} -> {final_count}")
                return True
            else:
                self.log_test("Message Persistence", False, f"Messages not persisted. Count: {initial_count} -> {final_count}")
                return False
                
        except Exception as e:
            self.log_test("Message Persistence", False, f"Error: {str(e)}")
            return False
    
    def run_all_tests(self):
        """Run all backend tests"""
        print("🚀 Starting WhatsApp AI Clone Backend Tests")
        print("=" * 60)
        
        # Test 1: API Health
        if not self.test_api_health():
            print("❌ API is not accessible. Stopping tests.")
            return self.get_summary()
        
        # Test 2: Get Chats
        if not self.test_get_chats():
            print("❌ Failed to get chats. Stopping tests.")
            return self.get_summary()
        
        # Test 3: Test specific AI personalities
        personality_tests = [
            ('alex_sarcastic', "You're so funny!", ['sarcastic', 'witty', 'joke', 'funny']),
            ('maya_mentor', "I need guidance in my career", ['guidance', 'advice', 'wisdom', 'help']),
            ('zoe_tech', "What do you think about Python programming?", ['python', 'code', 'programming', 'tech']),
            ('ryan_flirty', "How are you doing today?", ['charming', 'flirt', 'special', 'playful'])
        ]
        
        for personality, message, traits in personality_tests:
            self.test_send_message_to_personality(personality, message, traits)
            time.sleep(1)  # Small delay between tests
        
        # Test 4: Get chat messages for each personality
        for personality in ['alex_sarcastic', 'maya_mentor', 'zoe_tech', 'ryan_flirty']:
            self.test_get_chat_messages(personality)
        
        # Test 5: OpenAI Integration
        self.test_openai_integration()
        
        # Test 6: Message Persistence
        self.test_message_persistence()
        
        return self.get_summary()
    
    def get_summary(self):
        """Get test summary"""
        print("\n" + "=" * 60)
        print("📊 TEST SUMMARY")
        print("=" * 60)
        print(f"Total Tests: {self.test_results['total_tests']}")
        print(f"Passed: {self.test_results['passed_tests']}")
        print(f"Failed: {self.test_results['failed_tests']}")
        
        if self.test_results['failed_tests'] > 0:
            print("\n❌ FAILED TESTS:")
            for error in self.test_results['errors']:
                print(f"  - {error}")
        
        success_rate = (self.test_results['passed_tests'] / self.test_results['total_tests']) * 100 if self.test_results['total_tests'] > 0 else 0
        print(f"\nSuccess Rate: {success_rate:.1f}%")
        
        if success_rate >= 80:
            print("🎉 Backend is working well!")
        elif success_rate >= 60:
            print("⚠️  Backend has some issues but core functionality works")
        else:
            print("🚨 Backend has significant issues")
        
        return self.test_results

if __name__ == "__main__":
    tester = WhatsAppAITester()
    results = tester.run_all_tests()