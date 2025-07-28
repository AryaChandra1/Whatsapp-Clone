import React, { useState, useEffect } from 'react';
import {
  View,
  Text,
  FlatList,
  TouchableOpacity,
  StyleSheet,
  SafeAreaView,
  StatusBar,
  Image,
  Alert,
  TextInput,
  ScrollView,
  ActivityIndicator,
  Platform,
} from 'react-native';
import { router } from 'expo-router';
import Constants from 'expo-constants';
import { Ionicons } from '@expo/vector-icons';

const EXPO_PUBLIC_BACKEND_URL = Constants.expoConfig?.extra?.EXPO_PUBLIC_BACKEND_URL || process.env.EXPO_PUBLIC_BACKEND_URL;

interface Chat {
  id: string;
  ai_personality: string;
  name: string;
  avatar: string;
  description: string;
  last_message: string | null;
  last_message_time: string | null;
  last_seen: string;
  unread_count: number;
}

type FilterType = 'all' | 'unread' | 'favourites' | 'groups';

export default function ChatsScreen() {
  const [chats, setChats] = useState<Chat[]>([]);
  const [loading, setLoading] = useState(true);
  const [activeFilter, setActiveFilter] = useState<FilterType>('all');
  const [searchText, setSearchText] = useState('');

  useEffect(() => {
    loadChats();
  }, []);

  const loadChats = async () => {
    try {
      const response = await fetch(`${EXPO_PUBLIC_BACKEND_URL}/api/chats`);
      if (!response.ok) {
        throw new Error('Failed to load chats');
      }
      const chatsData = await response.json();
      setChats(chatsData);
    } catch (error) {
      console.error('Error loading chats:', error);
      Alert.alert('Error', 'Failed to load chats. Please try again.');
    } finally {
      setLoading(false);
    }
  };

  const formatTime = (timestamp: string | null) => {
    if (!timestamp) return '';
    const date = new Date(timestamp);
    const now = new Date();
    const diff = now.getTime() - date.getTime();
    const minutes = Math.floor(diff / 60000);
    const hours = Math.floor(diff / 3600000);
    const days = Math.floor(diff / 86400000);

    if (minutes < 1) return 'now';
    if (minutes < 60) return `${minutes}m ago`;
    if (hours < 24) return `${hours}h ago`;
    if (days < 7) return `${days}d ago`;
    
    // Format as time for recent messages
    const today = new Date();
    if (date.toDateString() === today.toDateString()) {
      return date.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit', hour12: true });
    }
    
    return date.toLocaleDateString();
  };

  const getFilteredChats = () => {
    let filteredChats = chats;
    
    if (activeFilter === 'unread') {
      filteredChats = chats.filter(chat => chat.unread_count > 0);
    }
    
    if (searchText) {
      filteredChats = filteredChats.filter(chat => 
        chat.name.toLowerCase().includes(searchText.toLowerCase()) ||
        chat.last_message?.toLowerCase().includes(searchText.toLowerCase())
      );
    }
    
    return filteredChats;
  };

  const renderFilterPill = (filter: FilterType, label: string, count?: number) => (
    <TouchableOpacity
      key={filter}
      style={[
        styles.filterPill,
        activeFilter === filter && styles.activeFilterPill
      ]}
      onPress={() => setActiveFilter(filter)}
    >
      <Text style={[
        styles.filterText,
        activeFilter === filter && styles.activeFilterText
      ]}>
        {label} {count ? count : ''}
      </Text>
    </TouchableOpacity>
  );

  const renderChatItem = ({ item }: { item: Chat }) => {
    const isUnread = item.unread_count > 0;
    
    return (
      <TouchableOpacity
        style={styles.chatItem}
        onPress={() => router.push(`/chat/${item.id}?name=${item.name}&personality=${item.ai_personality}`)}
        activeOpacity={0.7}
      >
        <View style={styles.avatarContainer}>
          <Image 
            source={{ uri: item.avatar }} 
            style={styles.avatar}
          />
          {item.last_seen === 'online' && <View style={styles.onlineIndicator} />}
        </View>
        
        <View style={styles.chatContent}>
          <View style={styles.chatHeader}>
            <Text style={[styles.chatName, isUnread && styles.unreadChatName]}>
              {item.name}
            </Text>
            <Text style={styles.chatTime}>
              {formatTime(item.last_message_time)}
            </Text>
          </View>
          
          <View style={styles.chatPreview}>
            <Text style={[styles.chatMessage, isUnread && styles.unreadChatMessage]} numberOfLines={1}>
              {item.last_message ? `You: ${item.last_message}` : item.description}
            </Text>
            {item.unread_count > 0 && (
              <View style={styles.unreadBadge}>
                <Text style={styles.unreadText}>{item.unread_count}</Text>
              </View>
            )}
          </View>
        </View>
      </TouchableOpacity>
    );
  };

  if (loading) {
    return (
      <SafeAreaView style={styles.container}>
        <StatusBar barStyle="dark-content" backgroundColor="#FFFFFF" />
        <View style={styles.header}>
          <Text style={styles.headerTitle}>Chats</Text>
          <View style={styles.headerActions}>
            <TouchableOpacity style={styles.headerButton}>
              <Ionicons name="camera-outline" size={24} color="#007AFF" />
            </TouchableOpacity>
            <TouchableOpacity style={styles.headerButton}>
              <Ionicons name="add-outline" size={28} color="#25D366" />
            </TouchableOpacity>
          </View>
        </View>
        <View style={styles.loadingContainer}>
          <ActivityIndicator size="large" color="#25D366" />
          <Text style={styles.loadingText}>Loading your conversations...</Text>
        </View>
      </SafeAreaView>
    );
  }

  const filteredChats = getFilteredChats();
  const unreadCount = chats.filter(chat => chat.unread_count > 0).length;

  return (
    <SafeAreaView style={styles.container}>
      <StatusBar barStyle="dark-content" backgroundColor="#FFFFFF" />
      
      <View style={styles.header}>
        <Text style={styles.headerTitle}>Chats</Text>
        <View style={styles.headerActions}>
          <TouchableOpacity style={styles.headerButton}>
            <Ionicons name="camera-outline" size={24} color="#007AFF" />
          </TouchableOpacity>
          <TouchableOpacity style={styles.headerButton}>
            <Ionicons name="add-outline" size={28} color="#25D366" />
          </TouchableOpacity>
        </View>
      </View>

      <View style={styles.searchContainer}>
        <View style={styles.searchBar}>
          <Ionicons name="search" size={20} color="#8E8E93" style={styles.searchIcon} />
          <TextInput
            style={styles.searchInput}
            placeholder="Ask Meta AI or Search"
            placeholderTextColor="#8E8E93"
            value={searchText}
            onChangeText={setSearchText}
          />
        </View>
      </View>

      <ScrollView horizontal showsHorizontalScrollIndicator={false} style={styles.filtersContainer}>
        <View style={styles.filtersContent}>
          {renderFilterPill('all', 'All')}
          {renderFilterPill('unread', 'Unread', unreadCount)}
          {renderFilterPill('favourites', 'Favourites', 1)}
          {renderFilterPill('groups', 'Groups')}
        </View>
      </ScrollView>

      <FlatList
        data={filteredChats}
        renderItem={renderChatItem}
        keyExtractor={(item) => item.id}
        style={styles.chatList}
        showsVerticalScrollIndicator={false}
        contentContainerStyle={styles.chatListContent}
      />
    </SafeAreaView>
  );
}

const styles = StyleSheet.create({
  container: {
    flex: 1,
    backgroundColor: '#FFFFFF',
  },
  header: {
    paddingHorizontal: 16,
    paddingVertical: 8,
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
  },
  headerTitle: {
    fontSize: 34,
    fontWeight: '700',
    color: '#000000',
    letterSpacing: -0.5,
    fontFamily: Platform.OS === 'ios' ? 'System' : 'sans-serif',
  },
  headerActions: {
    flexDirection: 'row',
    alignItems: 'center',
  },
  headerButton: {
    padding: 8,
    marginLeft: 4,
  },
  searchContainer: {
    paddingHorizontal: 16,
    paddingBottom: 12,
  },
  searchBar: {
    backgroundColor: '#F2F2F7',
    borderRadius: 10,
    flexDirection: 'row',
    alignItems: 'center',
    paddingHorizontal: 12,
    height: 44,
  },
  searchIcon: {
    marginRight: 8,
  },
  searchInput: {
    flex: 1,
    fontSize: 17,
    color: '#000000',
    fontFamily: Platform.OS === 'ios' ? 'System' : 'sans-serif',
  },
  filtersContainer: {
    paddingHorizontal: 16,
    marginBottom: 4,
  },
  filtersContent: {
    flexDirection: 'row',
    paddingRight: 16,
    alignItems: 'flex-start',
  },
  filterPill: {
    backgroundColor: '#F2F2F7',
    borderRadius: 12,
    paddingHorizontal: 12,
    paddingVertical: 2,
    marginRight: 8,
    flexGrow: 0,
    flexShrink: 0,
    alignSelf: 'flex-start',
  },
  activeFilterPill: {
    backgroundColor: '#25D366',
  },
  filterText: {
    fontSize: 14,
    fontWeight: '500',
    color: '#000000',
    fontFamily: Platform.OS === 'ios' ? 'System' : 'sans-serif',
  },
  activeFilterText: {
    color: '#FFFFFF',
  },
  loadingContainer: {
    flex: 1,
    justifyContent: 'center',
    alignItems: 'center',
    backgroundColor: '#F8F9FA',
  },
  loadingText: {
    fontSize: 16,
    color: '#666',
    marginTop: 16,
  },
  chatList: {
    flex: 1,
  },
  chatListContent: {
    paddingBottom: 2,
  },
  chatItem: {
    flexDirection: 'row',
    paddingHorizontal: 16,
    paddingVertical: 12,
    alignItems: 'center',
    backgroundColor: '#FFFFFF',
  },
  avatarContainer: {
    position: 'relative',
    marginRight: 12,
  },
  avatar: {
    width: 56,
    height: 56,
    borderRadius: 28,
    backgroundColor: '#E1E1E1',
  },
  onlineIndicator: {
    position: 'absolute',
    bottom: 2,
    right: 2,
    width: 16,
    height: 16,
    borderRadius: 8,
    backgroundColor: '#25D366',
    borderWidth: 2,
    borderColor: '#FFFFFF',
  },
  chatContent: {
    flex: 1,
  },
  chatHeader: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
    marginBottom: 2,
  },
  chatName: {
    fontSize: 17,
    fontWeight: '400',
    color: '#000000',
    letterSpacing: -0.2,
    fontFamily: Platform.OS === 'ios' ? 'System' : 'sans-serif',
  },
  unreadChatName: {
    fontWeight: '600',
  },
  chatTime: {
    fontSize: 15,
    color: '#8E8E93',
    fontWeight: '400',
    fontFamily: Platform.OS === 'ios' ? 'System' : 'sans-serif',
  },
  chatPreview: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
  },
  chatMessage: {
    fontSize: 15,
    color: '#8E8E93',
    flex: 1,
    lineHeight: 20,
    fontFamily: Platform.OS === 'ios' ? 'System' : 'sans-serif',
  },
  unreadChatMessage: {
    color: '#000000',
    fontWeight: '500',
  },
  unreadBadge: {
    backgroundColor: '#25D366',
    borderRadius: 12,
    minWidth: 24,
    height: 24,
    justifyContent: 'center',
    alignItems: 'center',
    marginLeft: 8,
    paddingHorizontal: 8,
  },
  unreadText: {
    color: '#FFFFFF',
    fontSize: 13,
    fontWeight: '600',
  },
});