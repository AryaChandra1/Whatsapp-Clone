import React from 'react';
import { 
  View, 
  Text, 
  StyleSheet, 
  SafeAreaView, 
  StatusBar, 
  ScrollView,
  TouchableOpacity,
  TextInput,
  Image
} from 'react-native';
import { Ionicons } from '@expo/vector-icons';

interface CallEntry {
  id: string;
  name: string;
  avatar: string;
  type: 'incoming' | 'outgoing' | 'missed';
  callType: 'voice' | 'video';
  time: string;
}

export default function CallsScreen() {
  const favouriteContacts = [
    {
      id: '1',
      name: 'David Miller Tech',
      avatar: 'https://images.unsplash.com/photo-1507003211169-0a1dd7228f2d',
    }
  ];

  const recentCalls: CallEntry[] = [
    {
      id: '1',
      name: 'Sarah Business Pro',
      avatar: 'https://images.unsplash.com/photo-1494790108377-be9c29b29330',
      type: 'incoming',
      callType: 'voice',
      time: '6:40 PM'
    },
    {
      id: '2', 
      name: 'Michael Video Editor',
      avatar: 'https://images.unsplash.com/photo-1599566150163-29194dcaad36',
      type: 'outgoing',
      callType: 'video',
      time: '6:37 PM'
    },
    {
      id: '3',
      name: 'Michael Video Editor', 
      avatar: 'https://images.unsplash.com/photo-1599566150163-29194dcaad36',
      type: 'missed',
      callType: 'video',
      time: '6:27 PM'
    },
    {
      id: '4',
      name: 'Jennifer Emergency',
      avatar: 'https://images.unsplash.com/photo-1438761681033-6461ffad8d80',
      type: 'outgoing', 
      callType: 'voice',
      time: '5:57 PM'
    },
    {
      id: '5',
      name: 'Robert Urgent Call',
      avatar: 'https://images.unsplash.com/photo-1472099645785-5658abf4ff4e',
      type: 'incoming',
      callType: 'voice', 
      time: '5:54 PM'
    },
    {
      id: '6',
      name: 'Michael Video Editor',
      avatar: 'https://images.unsplash.com/photo-1599566150163-29194dcaad36',
      type: 'incoming',
      callType: 'video',
      time: '5:23 PM'
    }
  ];

  const getCallIcon = (type: string, callType: string) => {
    if (type === 'incoming') {
      return <Ionicons name="call-outline" size={16} color="#25D366" style={styles.callTypeIcon} />;
    } else if (type === 'outgoing') {
      return <Ionicons name="call-outline" size={16} color="#25D366" style={[styles.callTypeIcon, styles.outgoingIcon]} />;
    } else { // missed
      return <Ionicons name="call-outline" size={16} color="#FF3B30" style={styles.callTypeIcon} />;
    }
  };

  const getCallStatus = (type: string) => {
    switch (type) {
      case 'incoming': return 'Incoming';
      case 'outgoing': return 'Outgoing'; 
      case 'missed': return 'Missed';
      default: return '';
    }
  };

  const renderFavouriteContact = (contact: any) => (
    <View key={contact.id} style={styles.favouriteItem}>
      <View style={styles.favouriteLeft}>
        <Image source={{ uri: contact.avatar }} style={styles.favouriteAvatar} />
        <Text style={styles.favouriteName}>{contact.name}</Text>
      </View>
      <View style={styles.favouriteActions}>
        <TouchableOpacity style={styles.favouriteActionButton}>
          <Ionicons name="call" size={24} color="#25D366" />
        </TouchableOpacity>
        <TouchableOpacity style={styles.favouriteActionButton}>
          <Ionicons name="videocam" size={24} color="#25D366" />
        </TouchableOpacity>
      </View>
    </View>
  );

  const renderCallEntry = (call: CallEntry) => (
    <TouchableOpacity key={call.id} style={styles.callItem}>
      <Image source={{ uri: call.avatar }} style={styles.callAvatar} />
      <View style={styles.callContent}>
        <Text style={[styles.callName, call.type === 'missed' && styles.missedCallName]}>
          {call.name}
        </Text>
        <View style={styles.callInfo}>
          {getCallIcon(call.type, call.callType)}
          <Text style={[styles.callStatus, call.type === 'missed' && styles.missedCallStatus]}>
            {getCallStatus(call.type)}
          </Text>
        </View>
      </View>
      <View style={styles.callRight}>
        <Text style={styles.callTime}>{call.time}</Text>
        <TouchableOpacity style={styles.infoButton}>
          <Ionicons name="information-circle-outline" size={24} color="#007AFF" />
        </TouchableOpacity>
      </View>
    </TouchableOpacity>
  );

  return (
    <SafeAreaView style={styles.container}>
      <StatusBar barStyle="dark-content" backgroundColor="#FFFFFF" />
      
      <View style={styles.header}>
        <TouchableOpacity style={styles.menuButton}>
          <Ionicons name="ellipsis-horizontal" size={24} color="#000000" />
        </TouchableOpacity>
        <Text style={styles.headerTitle}>Calls</Text>
        <TouchableOpacity style={styles.addButton}>
          <Ionicons name="add" size={28} color="#FFFFFF" />
        </TouchableOpacity>
      </View>

      <ScrollView style={styles.content} showsVerticalScrollIndicator={false}>
        <View style={styles.searchContainer}>
          <View style={styles.searchBar}>
            <Ionicons name="search" size={20} color="#8E8E93" style={styles.searchIcon} />
            <TextInput
              style={styles.searchInput}
              placeholder="Search"
              placeholderTextColor="#8E8E93"
            />
          </View>
        </View>

        <View style={styles.section}>
          <View style={styles.sectionHeader}>
            <Text style={styles.sectionTitle}>Favourites</Text>
            <TouchableOpacity>
              <Text style={styles.moreButton}>More</Text>
            </TouchableOpacity>
          </View>
          {favouriteContacts.map(renderFavouriteContact)}
        </View>

        <View style={styles.section}>
          <Text style={styles.sectionTitle}>Recent</Text>
          {recentCalls.map(renderCallEntry)}
        </View>

        <View style={styles.bottomSpacing} />
      </ScrollView>
    </SafeAreaView>
  );
}

const styles = StyleSheet.create({
  container: {
    flex: 1,
    backgroundColor: '#FFFFFF',
  },
  header: {
    flexDirection: 'row',
    alignItems: 'center',
    justifyContent: 'space-between',
    paddingHorizontal: 16,
    paddingVertical: 8,
  },
  menuButton: {
    padding: 8,
  },
  headerTitle: {
    fontSize: 34,
    fontWeight: '700',
    color: '#000000',
    letterSpacing: -0.5,
    flex: 1,
    textAlign: 'left',
    marginLeft: 8,
  },
  addButton: {
    backgroundColor: '#25D366',
    borderRadius: 20,
    width: 40,
    height: 40,
    justifyContent: 'center',
    alignItems: 'center',
  },
  content: {
    flex: 1,
  },
  searchContainer: {
    paddingHorizontal: 16,
    paddingBottom: 16,
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
  },
  section: {
    marginBottom: 32,
  },
  sectionHeader: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
    paddingHorizontal: 16,
    marginBottom: 16,
  },
  sectionTitle: {
    fontSize: 20,
    fontWeight: '600',
    color: '#000000',
  },
  moreButton: {
    fontSize: 17,
    color: '#007AFF',
    fontWeight: '400',
  },
  favouriteItem: {
    flexDirection: 'row',
    alignItems: 'center',
    justifyContent: 'space-between',
    paddingHorizontal: 16,
    paddingVertical: 12,
  },
  favouriteLeft: {
    flexDirection: 'row',
    alignItems: 'center',
    flex: 1,
  },
  favouriteAvatar: {
    width: 48,
    height: 48,
    borderRadius: 24,
    marginRight: 12,
  },
  favouriteName: {
    fontSize: 17,
    fontWeight: '400',
    color: '#000000',
    flex: 1,
  },
  favouriteActions: {
    flexDirection: 'row',
  },
  favouriteActionButton: {
    padding: 8,
    marginLeft: 8,
  },
  callItem: {
    flexDirection: 'row',
    alignItems: 'center',
    paddingHorizontal: 16,
    paddingVertical: 12,
  },
  callAvatar: {
    width: 48,
    height: 48,
    borderRadius: 24,
    marginRight: 12,
  },
  callContent: {
    flex: 1,
  },
  callName: {
    fontSize: 17,
    fontWeight: '400',
    color: '#000000',
    marginBottom: 2,
  },
  missedCallName: {
    color: '#FF3B30',
  },
  callInfo: {
    flexDirection: 'row',
    alignItems: 'center',
  },
  callTypeIcon: {
    marginRight: 6,
  },
  outgoingIcon: {
    transform: [{ rotate: '45deg' }],
  },
  callStatus: {
    fontSize: 15,
    color: '#8E8E93',
  },
  missedCallStatus: {
    color: '#FF3B30',
  },
  callRight: {
    alignItems: 'flex-end',
  },
  callTime: {
    fontSize: 15,
    color: '#8E8E93',
    marginBottom: 4,
  },
  infoButton: {
    padding: 4,
  },
  bottomSpacing: {
    height: 100,
  },
});