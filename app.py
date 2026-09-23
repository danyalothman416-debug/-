import React, { useState } from 'react';
import {
  StyleSheet,
  Text,
  View,
  TextInput,
  TouchableOpacity,
  FlatList,
  Image,
  Linking,
  SafeAreaView,
  StatusBar,
  ScrollView,
} from 'react-native';

const INITIAL_PLACES = [
  {
    id: '1',
    name: 'قەڵای کەرکووک',
    category: 'مێژوویی',
    rating: '4.9',
    address: 'سەنتەری شار، بەرامبەر قەیسەری',
    desc: 'دێرینترین هێمای مێژوویی شارەکە کە دەڕوانێت بەسەر تەواوی شاردا و مێژووەکەی بۆ هەزاران ساڵ لەمەوبەر دەگەڕێتەوە.',
    phone: '',
    image: 'https://images.unsplash.com/photo-1541872703-74c5e44368f9?auto=format&fit=crop&w=800&q=80',
    mapQuery: 'Kirkuk Citadel'
  },
  {
    id: '2',
    name: 'گەڕەکی ڕەحیماوا',
    category: 'گەڕەکەکان',
    rating: '4.8',
    address: 'باکووری کەرکووک',
    desc: 'گەڕەکێکی گەورە و زۆر قەرەباڵغ کە بە بازاڕی شەوانە و خواردنە میللییە بەتامەکانی ناسراوە.',
    phone: '',
    image: 'https://images.unsplash.com/photo-1519501025264-65ba15a82390?auto=format&fit=crop&w=800&q=80',
    mapQuery: 'Rahimawa Kirkuk'
  },
  {
    id: '3',
    name: 'گەڕەکی شۆرجە',
    category: 'گەڕەکەکان',
    rating: '4.7',
    address: 'ناوەندی شار',
    desc: 'گەڕەکێکی دێرین و بازرگانیی کەرکووک کە پێگەیەکی جوگرافی و مێژوویی تایبەتی لە شارەکەدا هەیە.',
    phone: '',
    image: 'https://images.unsplash.com/photo-1477959858617-67f30bc75b82?auto=format&fit=crop&w=800&q=80',
    mapQuery: 'Shorja Kirkuk'
  },
  {
    id: '4',
    name: 'گەڕەکی ئەڵماس',
    category: 'گەڕەکەکان',
    rating: '4.8',
    address: 'سەنتەری شاری کەرکووک',
    desc: 'ناوەندێکی مۆدێرنی شار کە پڕە لە نۆرینگە، دەرمانخانە، کافێ و خواردنگە هاوچەرخەکان.',
    phone: '',
    image: 'https://images.unsplash.com/photo-1486406146926-c627a92ad1ab?auto=format&fit=crop&w=800&q=80',
    mapQuery: 'Almas Kirkuk'
  },
  {
    id: '5',
    name: 'پارکی گشتی (باخچەی شار)',
    category: 'سەیران و پارک',
    rating: '4.6',
    address: 'ناوەندی شاری کەرکووک',
    desc: 'گەورەترین باخچەی مێژوویی شار بۆ پشوودانی خێزانەکان، پیاسەکردن و کات بەسەربردن.',
    phone: '',
    image: 'https://images.unsplash.com/photo-1519331379826-f10be5486c6f?auto=format&fit=crop&w=800&q=80',
    mapQuery: 'Kirkuk Public Park'
  },
  {
    id: '6',
    name: 'چێشتخانەی کەبابی خاسە',
    category: 'خواردن و ڕێستۆرانت',
    rating: '4.9',
    address: 'شەقامی سەرەکی قەڵا',
    desc: 'بەناوبانگترین کەبابی کەرکووک بە گۆشتی تازە و لەسەر خەڵووز لەگەڵ نانی گەرم و ترشیات.',
    phone: '07701234567',
    image: 'https://images.unsplash.com/photo-1555939594-58d7cb561ad1?auto=format&fit=crop&w=800&q=80',
    mapQuery: 'Kirkuk Kebab'
  },
  {
    id: '7',
    name: 'کەرکووک مۆڵ (Kirkuk Mall)',
    category: 'بازاڕ و مۆڵ',
    rating: '4.7',
    address: 'شەقامی ڕێگای بەغدا',
    desc: 'مۆڵێکی گەورەی هاوچەرخ بۆ بازاڕکردنی جلوبەرگ، براندە نێودەوڵەتییەکان و سینەما.',
    phone: '07709876543',
    image: 'https://images.unsplash.com/photo-1567449303078-57ad995bd301?auto=format&fit=crop&w=800&q=80',
    mapQuery: 'Kirkuk Mall'
  },
  {
    id: '8',
    name: 'فریاکەوتنی نەخۆشخانەی ئازادی',
    category: 'فریاگوزاری',
    rating: '4.5',
    address: 'گەڕەکی ئازادی',
    desc: 'خزمەتگوزاری پزیشکی بەپەلە و فریاکەوتن بە شێوەی ٢٤ کاتژمێری بۆ سەرجەم هاوڵاتییان.',
    phone: '122',
    image: 'https://images.unsplash.com/photo-1587351021759-3e566b6af7cc?auto=format&fit=crop&w=800&q=80',
    mapQuery: 'Azadi Hospital Kirkuk'
  }
];

const CATEGORIES = ['هەمووی', 'گەڕەکەکان', 'مێژوویی', 'سەیران و پارک', 'خواردن و ڕێستۆرانت', 'بازاڕ و مۆڵ', 'فریاگوزاری'];

export default function App() {
  const [places, setPlaces] = useState(INITIAL_PLACES);
  const [search, setSearch] = useState('');
  const [selectedCat, setSelectedCat] = useState('هەمووی');
  const [favorites, setFavorites] = useState([]);
  const [isDark, setIsDark] = useState(false);

  const toggleFavorite = (id) => {
    if (favorites.includes(id)) {
      setFavorites(favorites.filter((fId) => fId !== id));
    } else {
      setFavorites([...favorites, id]);
    }
  };

  const openMap = (query) => {
    const url = `https://www.google.com/maps/search/?api=1&query=${encodeURIComponent(query + ' Kirkuk')}`;
    Linking.openURL(url);
  };

  const callPhone = (phone) => {
    if (phone) Linking.openURL(`tel:${phone}`);
  };

  const filteredPlaces = places.filter((item) => {
    const matchesCat = selectedCat === 'هەمووی' || item.category === selectedCat;
    const matchesSearch =
      item.name.includes(search) ||
      item.desc.includes(search) ||
      item.address.includes(search);
    return matchesCat && matchesSearch;
  });

  const theme = {
    bg: isDark ? '#0b0f19' : '#f8fafc',
    cardBg: isDark ? '#1e293b' : '#ffffff',
    text: isDark ? '#f8fafc' : '#0f172a',
    subText: isDark ? '#94a3b8' : '#64748b',
    border: isDark ? '#334155' : '#e2e8f0',
  };

  return (
    <SafeAreaView style={[styles.container, { backgroundColor: theme.bg }]}>
      <StatusBar barStyle={isDark ? 'light-content' : 'dark-content'} />

      {/* بەشی سەرپەڕە */}
      <View style={[styles.header, { backgroundColor: theme.cardBg, borderColor: theme.border }]}>
        <View style={styles.headerTop}>
          <TouchableOpacity onPress={() => setIsDark(!isDark)} style={styles.iconBtn}>
            <Text style={styles.iconTxt}>{isDark ? '☀️' : '🌙'}</Text>
          </TouchableOpacity>
          <View style={{ alignItems: 'flex-end' }}>
            <Text style={[styles.appTitle, { color: theme.text }]}>ڕێبەری کەرکووک</Text>
            <Text style={[styles.appSub, { color: theme.subText }]}>دەروازەی تەواوی شار و گەڕەکەکان</Text>
          </View>
        </View>

        {/* بۆکسی گەڕان */}
        <TextInput
          style={[styles.searchInput, { backgroundColor: theme.bg, color: theme.text, borderColor: theme.border }]}
          placeholder="گەڕان بۆ هەر شوێنێک یان گەڕەکێک..."
          placeholderTextColor={theme.subText}
          value={search}
          onChangeText={setSearch}
        />

        {/* لیستی پۆلەکان */}
        <ScrollView horizontal showsHorizontalScrollIndicator={false} style={styles.catScroll}>
          {CATEGORIES.map((cat) => (
            <TouchableOpacity
              key={cat}
              onPress={() => setSelectedCat(cat)}
              style={[
                styles.catBadge,
                selectedCat === cat ? styles.catBadgeActive : { backgroundColor: theme.bg, borderColor: theme.border },
              ]}
            >
              <Text
                style={[
                  styles.catTxt,
                  selectedCat === cat ? styles.catTxtActive : { color: theme.subText },
                ]}
              >
                {cat}
              </Text>
            </TouchableOpacity>
          ))}
        </ScrollView>
      </View>

      {/* کاردەکان */}
      <FlatList
        data={filteredPlaces}
        keyExtractor={(item) => item.id}
        contentContainerStyle={{ padding: 16, paddingBottom: 40 }}
        renderItem={({ item }) => {
          const isFav = favorites.includes(item.id);
          return (
            <View style={[styles.card, { backgroundColor: theme.cardBg, borderColor: theme.border }]}>
              <View style={styles.imageBox}>
                <Image source={{ uri: item.image }} style={styles.cardImg} />
                <TouchableOpacity
                  style={styles.favBtn}
                  onPress={() => toggleFavorite(item.id)}
                >
                  <Text style={{ fontSize: 16 }}>{isFav ? '❤️' : '🤍'}</Text>
                </TouchableOpacity>
                <View style={styles.ratingBadge}>
                  <Text style={styles.ratingTxt}>⭐ {item.rating}</Text>
                </View>
              </View>

              <View style={styles.cardContent}>
                <View style={styles.cardHeaderRow}>
                  <Text style={[styles.cardTag, { color: '#0284c7' }]}>{item.category}</Text>
                  <Text style={[styles.cardTitle, { color: theme.text }]}>{item.name}</Text>
                </View>
                <Text style={[styles.cardLoc, { color: theme.subText }]}>📍 {item.address}</Text>
                <Text style={[styles.cardDesc, { color: theme.subText }]}>{item.desc}</Text>

                {/* دوگمە کردارەکان */}
                <View style={[styles.actionRow, { borderTopColor: theme.border }]}>
                  <TouchableOpacity
                    style={styles.mapBtn}
                    onPress={() => openMap(item.mapQuery)}
                  >
                    <Text style={styles.mapBtnTxt}>🗺️ نەخشە</Text>
                  </TouchableOpacity>

                  {item.phone ? (
                    <TouchableOpacity
                      style={styles.callBtn}
                      onPress={() => callPhone(item.phone)}
                    >
                      <Text style={styles.callBtnTxt}>📞 پەیوەندی</Text>
                    </TouchableOpacity>
                  ) : null}
                </View>
              </View>
            </View>
          );
        }}
      />
    </SafeAreaView>
  );
}

const styles = StyleSheet.create({
  container: { flex: 1 },
  header: { padding: 16, borderBottomWidth: 1 },
  headerTop: { flexDirection: 'row', justifyContent: 'space-between', alignItems: 'center', marginBottom: 12 },
  appTitle: { fontSize: 22, fontWeight: 'bold' },
  appSub: { fontSize: 12, marginTop: 2 },
  iconBtn: { padding: 8, borderRadius: 12, backgroundColor: '#f1f5f9' },
  iconTxt: { fontSize: 18 },
  searchInput: {
    height: 44,
    borderRadius: 22,
    borderWidth: 1,
    paddingHorizontal: 16,
    textAlign: 'right',
    fontSize: 14,
    marginBottom: 10,
  },
  catScroll: { marginTop: 4 },
  catBadge: { paddingHorizontal: 14, paddingVertical: 6, borderRadius: 20, borderWidth: 1, marginRight: 8 },
  catBadgeActive: { backgroundColor: '#0284c7', borderColor: '#0284c7' },
  catTxt: { fontSize: 12, fontWeight: 'bold' },
  catTxtActive: { color: '#ffffff' },
  card: { borderRadius: 20, borderWidth: 1, marginBottom: 16, overflow: 'hidden' },
  imageBox: { height: 180, width: '100%', position: 'relative' },
  cardImg: { width: '100%', height: '100%' },
  favBtn: {
    position: 'absolute',
    top: 12,
    left: 12,
    backgroundColor: 'rgba(255,255,255,0.9)',
    width: 36,
    height: 36,
    borderRadius: 18,
    alignItems: 'center',
    justifyContent: 'center',
  },
  ratingBadge: {
    position: 'absolute',
    bottom: 12,
    right: 12,
    backgroundColor: 'rgba(0,0,0,0.65)',
    paddingHorizontal: 10,
    paddingVertical: 4,
    borderRadius: 12,
  },
  ratingTxt: { color: '#fff', fontSize: 12, fontWeight: 'bold' },
  cardContent: { padding: 16 },
  cardHeaderRow: { flexDirection: 'row', justifyContent: 'space-between', alignItems: 'center', marginBottom: 4 },
  cardTitle: { fontSize: 18, fontWeight: 'bold' },
  cardTag: { fontSize: 12, fontWeight: 'bold' },
  cardLoc: { fontSize: 12, marginBottom: 8, textAlign: 'right' },
  cardDesc: { fontSize: 13, lineHeight: 20, textAlign: 'right', marginBottom: 14 },
  actionRow: { flexDirection: 'row', paddingTop: 12, borderTopWidth: 1, gap: 10 },
  mapBtn: {
    flex: 1,
    backgroundColor: '#0284c7',
    paddingVertical: 10,
    borderRadius: 12,
    alignItems: 'center',
  },
  mapBtnTxt: { color: '#fff', fontSize: 13, fontWeight: 'bold' },
  callBtn: {
    backgroundColor: '#10b981',
    paddingHorizontal: 16,
    paddingVertical: 10,
    borderRadius: 12,
    alignItems: 'center',
  },
  callBtnTxt: { color: '#fff', fontSize: 13, fontWeight: 'bold' },
});
