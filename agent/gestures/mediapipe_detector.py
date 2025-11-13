import cv2
import mediapipe as mp
import numpy as np
import logging
from typing import List, Optional, Tuple, Dict, Any
from dataclasses import dataclass
import time


@dataclass
class GestureResult:
    gesture_code: str
    confidence: float
    landmarks: List[Tuple[float, float, float]]
    timestamp: float
    bbox: Optional[Tuple[int, int, int, int]] = None  # (x, y, w, h)


class MediaPipeGestureDetector:
    def __init__(self,
                 min_detection_confidence: float = 0.5,
                 min_tracking_confidence: float = 0.5,
                 max_hands: int = 2):
        self.mp_hands = mp.solutions.hands
        self.mp_drawing = mp.solutions.drawing_utils
        self.mp_drawing_styles = mp.solutions.drawing_styles
        
        self.hands = self.mp_hands.Hands(
            static_image_mode=False,
            max_num_hands=max_hands,
            min_detection_confidence=min_detection_confidence,
            min_tracking_confidence=min_tracking_confidence
        )
        
        self.last_gesture_time = 0
        self.gesture_cooldown = 1.0  # seconds between gestures
        
        logging.info('MediaPipe gesture detector initialized')
    
    def detect_hands(self, image: np.ndarray) -> Optional[List[GestureResult]]:
        if image is None:
            return None
            
        # Convert BGR to RGB
        rgb_image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
        results = self.hands.process(rgb_image)
        
        if not results.multi_hand_landmarks:
            return None
            
        gestures = []
        current_time = time.time()
        
        for hand_idx, hand_landmarks in enumerate(results.multi_hand_landmarks):
            # Extract landmark coordinates
            landmarks = [(lm.x, lm.y, lm.z) for lm in hand_landmarks.landmark]
            
            # Calculate bounding box
            h, w = image.shape[:2]
            x_coords = [int(lm.x * w) for lm in hand_landmarks.landmark]
            y_coords = [int(lm.y * h) for lm in hand_landmarks.landmark]
            bbox = (min(x_coords), min(y_coords), max(x_coords) - min(x_coords), max(y_coords) - min(y_coords))
            
            # Recognize gesture
            gesture_code, confidence = self._recognize_gesture(landmarks)
            
            if gesture_code and confidence > 0.6:
                # Check cooldown to avoid repeated gestures
                if current_time - self.last_gesture_time > self.gesture_cooldown:
                    gestures.append(GestureResult(
                        gesture_code=gesture_code,
                        confidence=confidence,
                        landmarks=landmarks,
                        timestamp=current_time,
                        bbox=bbox
                    ))
                    self.last_gesture_time = current_time
        
        return gestures if gestures else None
    
    def _recognize_gesture(self, landmarks: List[Tuple[float, float, float]]) -> Tuple[Optional[str], float]:
        if not landmarks or len(landmarks) < 21:
            return None, 0.0
            
        # Get fingertip and base positions for each finger
        finger_states = self._get_finger_states(landmarks)
        
        # Define gestures based on finger states
        if self._is_pointing_up(finger_states):
            return 'POINT_UP', 0.9
        elif self._is_pointing_index(finger_states):
            return 'POINT_INDEX', 0.9
        elif self._is_thumbs_up(finger_states):
            return 'THUMBS_UP', 0.9
        elif self._is_thumbs_down(finger_states):
            return 'THUMBS_DOWN', 0.9
        elif self._is_open_palm(finger_states):
            return 'OPEN_PALM', 0.8
        elif self._is_closed_fist(finger_states):
            return 'CLOSED_FIST', 0.9
        elif self._is_victory(finger_states):
            return 'VICTORY', 0.9
        elif self._is_ok_sign(landmarks):
            return 'OK_SIGN', 0.8
            
        return None, 0.0
    
    def _get_finger_states(self, landmarks: List[Tuple[float, float, float]]) -> Dict[str, bool]:
        # Finger tip and base indices
        finger_tips = [4, 8, 12, 16, 20]  # thumb, index, middle, ring, pinky
        finger_bases = [3, 6, 10, 14, 18]
        
        finger_states = {}
        finger_names = ['thumb', 'index', 'middle', 'ring', 'pinky']
        
        for i, name in enumerate(finger_names):
            tip_y = landmarks[finger_tips[i]][1]
            base_y = landmarks[finger_bases[i]][1]
            
            # For thumb, check x direction instead of y
            if name == 'thumb':
                tip_x = landmarks[finger_tips[i]][0]
                base_x = landmarks[finger_bases[i]][0]
                finger_states[name] = tip_x > base_x
            else:
                finger_states[name] = tip_y < base_y
        
        return finger_states
    
    def _is_pointing_up(self, finger_states: Dict[str, bool]) -> bool:
        return (finger_states['index'] and not finger_states['middle'] and
                not finger_states['ring'] and not finger_states['pinky'] and
                not finger_states['thumb'])
    
    def _is_pointing_index(self, finger_states: Dict[str, bool]) -> bool:
        return (finger_states['index'] and not finger_states['middle'] and
                not finger_states['ring'] and not finger_states['pinky'])
    
    def _is_thumbs_up(self, finger_states: Dict[str, bool]) -> bool:
        return (finger_states['thumb'] and not finger_states['index'] and
                not finger_states['middle'] and not finger_states['ring'] and
                not finger_states['pinky'])
    
    def _is_thumbs_down(self, finger_states: Dict[str, bool]) -> bool:
        return (not finger_states['thumb'] and not finger_states['index'] and
                not finger_states['middle'] and not finger_states['ring'] and
                not finger_states['pinky'])
    
    def _is_open_palm(self, finger_states: Dict[str, bool]) -> bool:
        return all(finger_states.values())
    
    def _is_closed_fist(self, finger_states: Dict[str, bool]) -> bool:
        return not any(finger_states.values())
    
    def _is_victory(self, finger_states: Dict[str, bool]) -> bool:
        return (finger_states['index'] and finger_states['middle'] and
                not finger_states['ring'] and not finger_states['pinky'])
    
    def _is_ok_sign(self, landmarks: List[Tuple[float, float, float]]) -> bool:
        # Check if thumb and index finger form a circle (OK sign)
        thumb_tip = landmarks[4]
        index_tip = landmarks[8]
        distance = np.sqrt((thumb_tip[0] - index_tip[0])**2 + (thumb_tip[1] - index_tip[1])**2)
        return distance < 0.05
    
    def draw_landmarks(self, image: np.ndarray, hand_landmarks) -> np.ndarray:
        if hand_landmarks:
            self.mp_drawing.draw_landmarks(
                image,
                hand_landmarks,
                self.mp_hands.HAND_CONNECTIONS,
                self.mp_drawing_styles.get_default_hand_landmarks_style(),
                self.mp_drawing_styles.get_default_hand_connections_style()
            )
        return image
    
    def close(self):
        if self.hands is not None:
            self.hands.close()
            self.hands = None
    
    def __del__(self):
        try:
            self.close()
        except:
            pass


