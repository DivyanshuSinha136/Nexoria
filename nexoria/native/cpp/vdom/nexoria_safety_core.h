// C ABI for nexoria-safety-core (see nexoria/native/rust_safety/src/lib.rs).
// A generational string interner used by the native VDOM diff engine so
// diff-key comparisons in the C++ hot loop are integer equality checks,
// not raw C-string lifetime/comparison code.
#ifndef NEXORIA_SAFETY_CORE_H
#define NEXORIA_SAFETY_CORE_H

#include <stdint.h>
#include <stddef.h>

#ifdef __cplusplus
extern "C" {
#endif

typedef struct Interner Interner;

Interner *nx_interner_new(void);
void nx_interner_free(Interner *ptr);
uint32_t nx_interner_intern(Interner *ptr, const uint8_t *data, size_t len);
int64_t nx_interner_get_len(const Interner *ptr, uint32_t id);
const uint8_t *nx_interner_get_ptr(const Interner *ptr, uint32_t id);
int nx_interner_ids_equal(uint32_t a, uint32_t b);

#ifdef __cplusplus
}
#endif

#endif // NEXORIA_SAFETY_CORE_H
